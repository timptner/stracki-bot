import discord
import jwt
import re
import settings
from datetime import datetime, timedelta
from mail import verification_mail

client = discord.Client()


@client.event
async def on_ready():
    print(f"Liste der verbundenen Server:")
    for guild in client.guilds:
        print(f" - {guild.name}")


@client.event
async def on_message(message):
    # prevent message loops
    if message.author == client.user:
        return

    # me
    if message.content.startswith('$me'):
        response = f"Name: `{message.author}`\nID: `{message.author.id}`"
        await message.channel.send(response)

    # servers
    if message.content.startswith('$servers'):
        for guild in client.guilds:
            await message.channel.send(f"**{guild.name}** `{guild.id}`")

    # verify
    if message.content.startswith('$verify'):
        if message.guild:
            response = f"Dieser Befehl ist nur als private Nachricht erlaubt! <@{message.author.id}>"
            await message.channel.send(response)
            await message.delete()
            return

        pattern = re.compile(r'([a-z]+[0-9]?\.)?[a-z]+[0-9]?@(st\.)?ovgu\.de', re.IGNORECASE)
        match = re.search(pattern, message.content.lower())
        if match:
            payload = {
                'uid': message.author.id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=2),
            }
            token = jwt.encode(payload, settings.JWT_KEY, algorithm='HS256').decode('utf8').split('.')
            data = {
                'token_header': token[0],
                'token_payload': token[1],
                'token_signature': token[2],
                'user': str(message.author),
                'bot': str(client.user),
            }
            verification_mail(match.group(), data)
            await message.channel.send(f"Ich habe eine E-Mail zur Verifizierung an `{match.group()}` geschickt!")

        else:
            await message.channel.send("Es sind nur E-Mail Adressen der OVGU Magdeburg erlaubt! "
                                       "(z. Bsp. `jens.strackeljan@ovgu.de`)")

    # token
    if message.content.startswith('$token'):
        if message.guild:
            response = f"Dieser Befehl ist nur als private Nachricht erlaubt! <@{message.author.id}>"
            await message.channel.send(response)
            await message.delete()
            return

        pattern = re.compile(r'(\+[a-z0-9\-_]+\*\n?){3}', re.IGNORECASE)
        match = re.search(pattern, message.content)
        if match:
            token = match.group().replace('\n', '').replace(' ', '').replace('*+', '.')[1:-1]
            try:
                payload = jwt.decode(token, settings.JWT_KEY, algorithms=['HS256'])

            except jwt.exceptions.DecodeError:
                await message.channel.send("Der Token ist ungültig.")
                return

            except jwt.exceptions.ExpiredSignatureError:
                await message.channel.send("Der Token ist abgelaufen.")
                return

            if message.author.id != payload['uid']:
                await message.channel.send("Dieser Token ist von einem anderen Benutzer! Zugriff verweigert.")
                return

            user = discord.utils.get(client.users, id=payload['uid'])
            guilds_success = ''
            for guild in client.guilds:
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
                await message.channel.send(response + guilds_success)

            else:
                await message.channel.send("Ich konnte dir auf **keinem** Server die Rolle `Verifiziert` zuweisen!")

        else:
            await message.channel.send("So funktioniert das nicht! Bitte gib einen echten Token an.")

client.run(settings.BOT_TOKEN)
