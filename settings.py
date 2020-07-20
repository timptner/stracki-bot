from os import getenv
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Files
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR.joinpath('templates')

# Discord
BOT_TOKEN = getenv('DISCORD_BOT_TOKEN')

# E-Mail
mail = {
    'name': "Faking",
    'email': "noreply@faking.cool",
    'host': getenv('SMTP_HOST'),
    'port': getenv('SMTP_PORT'),
    'username': getenv('SMTP_USERNAME'),
    'password': getenv('SMTP_PASSWORD')
}

# JWT
JWT_KEY = getenv('JWT_SECRET')
