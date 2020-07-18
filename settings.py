from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Discord
bot_token = getenv('DISCORD_BOT_TOKEN')

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
jwt_key = getenv('JWT_SECRET')
