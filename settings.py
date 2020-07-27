import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Development
DEBUG = os.getenv('DEBUG')

# Files
BASE_DIR = Path(__file__).resolve().parent

# Discord
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TRUSTED_GUILDS = [int(guild) for guild in os.getenv('DISCORD_TRUSTED_GUILDS').split(',')]

# E-Mail
mail = {
    'name': "Faking",
    'email': "noreply@faking.cool",
    'host': os.getenv('SMTP_HOST'),
    'port': os.getenv('SMTP_PORT'),
    'username': os.getenv('SMTP_USERNAME'),
    'password': os.getenv('SMTP_PASSWORD')
}

# JWT
JWT_KEY = os.getenv('JWT_SECRET')
