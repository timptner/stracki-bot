from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Discord
TOKEN = getenv('DISCORD_BOT_TOKEN')
GUILD = getenv('DISCORD_GUILD_ID')
ROLE = getenv('DISCORD_ROLE_ID')

# E-Mail
MAIL_NAME = "Faking"
MAIL_EMAIL = "noreply@faking.cool"

MAIL_HOST = getenv('SMTP_HOST')
MAIL_PORT = getenv('SMTP_PORT')
MAIL_USER = getenv('SMTP_USER')
MAIL_PASS = getenv('SMTP_PASS')

# JWT
SECRET = getenv('SECRET')
