import discord
import jwt
import re
from datetime import datetime, timedelta
from mail import verification_mail
from settings import TOKEN, SECRET, GUILD, ROLE

client = discord.Client()


@client.event
async def on_ready():
    print(f"Verbindung zu Discord wurde hergestellt.")

    print(f"Liste der verbundenen Server:")
    for guild in client.guilds:
        print(f" - {guild.name} <{guild.id}>")


@client.event
async def on_message(message):
    # prevent message loops
    if message.author == client.user:
        return

    # verify
    if message.content.startswith('$verify'):
        pattern = re.compile(r'([a-z]+[0-9]?\.)?[a-z]+[0-9]?@(st\.)?ovgu\.de', re.IGNORECASE)
        match = re.search(pattern, message.content.lower())

        if match:
            payload = {
                'uid': message.author.id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=2),
            }
            token = jwt.encode(payload, SECRET, algorithm='HS256').decode('utf8')

            data = {
                'token': str(token),
                'user': str(message.author),
                'bot': str(client.user),
            }
            verification_mail(match.group(), data)

            await message.channel.send(f"Ich habe eine E-Mail zur Verifizierung an `{match.group()}` geschickt!")

        else:
            await message.channel.send("Es sind nur E-Mail Adressen der OVGU Magdeburg erlaubt! "\
                                       "(z. Bsp. `jens.strackeljan@ovgu.de`)")

    # token
    if message.content.startswith('$token'):
        pattern = re.compile(r'([a-z0-9\-_]+\.){2}[a-z0-9\-_]+', re.IGNORECASE)
        match = re.search(pattern, message.content)

        if match:
            try:
                payload = jwt.decode(match.group(), SECRET, algorithms=['HS256'])

            except jwt.exceptions.InvalidSignatureError:
                await message.channel.send("Der Token ist ungültig.")
                return

            except jwt.exceptions.ExpiredSignatureError:
                await message.channel.send("Der Token ist abgelaufen.")
                return

            guild = discord.utils.get(client.guilds, id=int(GUILD))
            member = guild.get_member(payload['uid'])
            role = guild.get_role(int(ROLE))

            await member.add_roles(role)

            await message.channel.send(f"Ich habe **{member}** die Rolle `{role}` zugewiesen.")

        else:
            await message.channel.send("Unbekannter Token.")

client.run(TOKEN)
