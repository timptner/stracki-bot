import discord
import jwt
import re

from datetime import datetime, timedelta
from discord.ext import commands

from .mail import verification_mail
from .settings import BOT_TOKEN, TRUSTED_GUILDS, JWT_KEY

bot = commands.Bot(command_prefix='$', description="The one and only! Jens f***ing Strackeljahn.")


def start():
    bot.run(BOT_TOKEN)


@bot.event
async def on_ready():
    print(f"Liste aller verbundenen Server. Mit 'x' markierte Server werden beobachtet.")
    for guild in bot.guilds:
        if guild.id in TRUSTED_GUILDS:
            print("[X] ", end='')

        else:
            print("[ ] ", end='')

        print(f"{guild.name} ({guild.id})")


@bot.check
async def trusted_server(ctx):
    # allow private messages
    if ctx.guild is None:
        return True

    # check if server is trusted
    return ctx.guild.id in TRUSTED_GUILDS


@bot.command()
async def about(ctx):
    await ctx.send("My creator is Aiven Timptner.")


@bot.command()
async def servers(ctx):
    # return all connected servers
    await ctx.send('\n'.join([guild.name for guild in bot.guilds]))


@bot.command()
@commands.dm_only()
async def verify(ctx, email):
    # validate email address
    pattern = re.compile(r'.*@(st\.)?ovgu\.de')
    match = re.fullmatch(pattern, email.lower())
    if match is None:
        await ctx.send("Es sind nur E-Mail Adressen der **OVGU Magdeburg** erlaubt! "
                       "(z. Bsp. `jens.strackeljan@ovgu.de`)")
        return

    # prepare token
    payload = {
        'uid': ctx.author.id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=2),
    }
    jwt_token = jwt.encode(payload, JWT_KEY, algorithm='HS256').decode('utf8').split('.')

    # prepare verification mail
    data = {
        'token_header': jwt_token[0],
        'token_payload': jwt_token[1],
        'token_signature': jwt_token[2],
        'user': ctx.author.name,
        'bot': bot.user.name,
    }
    verification_mail(match.group(0), data)

    # give feedback
    await ctx.send(f"Ich habe eine E-Mail zur Verifizierung an `{match.group(0).lower()}` geschickt!")


@bot.command()
@commands.dm_only()
async def token(ctx, header, payload, signature):
    # prepare token
    jwt_token = f'{header}.{payload}.{signature}'

    # decode token
    try:
        payload = jwt.decode(jwt_token, JWT_KEY, algorithms=['HS256'])

    # token is broken
    except jwt.exceptions.DecodeError:
        await ctx.send("Der Token ist ungültig.")
        return

    # token is too old
    except jwt.exceptions.ExpiredSignatureError:
        await ctx.send("Der Token ist abgelaufen.")
        return

    # token is from different user
    if ctx.author.id != payload['uid']:
        await ctx.send("Der Token ist von einem anderen Benutzer! Zugriff verweigert.")
        return

    # apply role to user on every guild
    guilds = []
    for guild in bot.guilds:
        # ignore untrusted guilds
        if guild.id not in TRUSTED_GUILDS:
            continue

        # check if user is member of guild
        member = guild.get_member(payload['uid'])
        if member is None:
            guilds.append((guild.name, "Kein Mitglied"))
            continue

        # check if role exists on guild
        role = discord.utils.get(guild.roles, name='Verifiziert')
        if role is None:
            guilds.append((guild.name, "Rolle nicht vorhanden"))
            await guild.owner.send(f"Die automatische Verifizierung ist fehlgeschlagen. "
                                   f"Auf deinem Server ({guild.name}) existiert keine Rolle `Verifiziert`!")
            continue

        # check if member already has role
        if role in member.roles:
            guilds.append((guild.name, "Rolle bereits zugewiesen"))
            continue

        # add role to member
        try:
            await member.add_roles(role)

        except discord.errors.Forbidden:
            guilds.append((guild.name, "Fehlende Berechtigung"))
            await guild.owner.send("Test")
            continue

        guilds.append((guild.name, "Erfolgreich"))

    # give feedback
    responses = [f"**{guild}** – {message}" for guild, message in guilds]
    await ctx.send("Ich habe dir auf folgenden Servern versucht die Rolle `Verifiziert` zuzuweisen:\n" +
                   '\n'.join(responses))


@verify.error
@token.error
async def handle_error(ctx, error):
    print(error)

    # guild messages only allowed as private message
    if isinstance(error, commands.PrivateMessageOnly):
        await ctx.message.delete()
        await ctx.send(f"Dieser Befehl ist nur als private Nachricht erlaubt! <@{ctx.author.id}>")

    # missing arguments
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Zu wenig Argumente für diesen Befehl!")