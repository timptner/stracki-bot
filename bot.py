import discord
import jwt
import re
import settings
from datetime import datetime, timedelta
from discord.ext import commands
from mail import verification_mail

bot = commands.Bot(command_prefix='$', description="The one and only! Jens f***ing Strackeljahn.")


@bot.event
async def on_ready():
    print(f"Liste aller verbundenen Server. Mit 'x' markierte Server werden beobachtet.")
    for guild in bot.guilds:
        if guild.id in settings.GUILDS:
            print(f" [X] {guild.name}")

        else:
            print(f" [ ] {guild.name}")


@bot.check
async def trusted_server(ctx):
    if ctx.guild is None:
        return True

    if ctx.guild.id in settings.GUILDS:
        return True

    await ctx.send("Dieser Server liegt nicht auf meinem Campus!")
    return False


@bot.command()
async def servers(ctx):
    await ctx.send('\n'.join([guild.name for guild in bot.guilds]))


@bot.command()
@commands.dm_only()
async def verify(ctx, arg):
    pattern = re.compile(r'^([a-z]+[0-9]?\.)?[a-z]+[0-9]?@(st\.)?ovgu\.de$')
    if re.match(pattern, arg.lower()):
        payload = {
            'uid': ctx.author.id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=2),
        }
        jwt_token = jwt.encode(payload, settings.JWT_KEY, algorithm='HS256').decode('utf8').split('.')
        data = {
            'token_header': jwt_token[0],
            'token_payload': jwt_token[1],
            'token_signature': jwt_token[2],
            'user': ctx.author.name,
            'bot': bot.user.name,
        }
        verification_mail(arg, data)
        await ctx.send(f"Ich habe eine E-Mail zur Verifizierung an `{arg.lower()}` geschickt!")

    else:
        await ctx.send("Es sind nur E-Mail Adressen der **OVGU Magdeburg** erlaubt! "
                       "(z. Bsp. `jens.strackeljan@ovgu.de`)")


@bot.command()
@commands.dm_only()
async def token(ctx, arg):
    pattern = re.compile(r'^(\+[a-z0-9\-_]+\*\n?){3}$', re.IGNORECASE)
    if re.match(pattern, arg):
        jwt_token = arg.replace('\n', '').replace(' ', '').replace('*+', '.')[1:-1]
        try:
            payload = jwt.decode(jwt_token, settings.JWT_KEY, algorithms=['HS256'])

        except jwt.exceptions.DecodeError:
            await ctx.send("Der Token ist ungültig.")
            return

        except jwt.exceptions.ExpiredSignatureError:
            await ctx.send("Der Token ist abgelaufen.")
            return

        if ctx.author.id != payload['uid']:
            await ctx.send("Dieser Token ist von einem anderen Benutzer! Zugriff verweigert.")
            return

        user = discord.utils.get(bot.users, id=payload['uid'])
        guilds_success = ''
        for guild in bot.guilds:
            member = guild.get_member(user.id)
            role = discord.utils.get(guild.roles, name='Verifiziert')
            if role and member:
                try:
                    await member.add_roles(role)

                except discord.errors.Forbidden:
                    print(f"Fehlende Berechtigung für Server '{guild}'.")

                else:
                    guilds_success += f"\n - {guild}"

        if guilds_success:
            response = "Ich habe dir auf den folgenden Servern die Rolle `Verifiziert` zugewiesen."
            await ctx.send(response + guilds_success)

        else:
            await ctx.send("Ich konnte dir auf **keinem** Server die Rolle `Verifiziert` zuweisen!")

    else:
        await ctx.send("So funktioniert das nicht! Bitte gib einen echten Token an.")


@verify.error
@token.error
async def handle_error(ctx, error):
    if isinstance(error, commands.PrivateMessageOnly):
        await ctx.message.delete()
        await ctx.send(f"Dieser Befehl ist nur als private Nachricht erlaubt! <@{ctx.author.id}>")

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Zu wenig Argumente für diesen Befehl!")

bot.run(settings.BOT_TOKEN)
