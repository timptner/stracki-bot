import smtplib
import markdown as md

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid

from .settings import MAIL, BASE_DIR


def verification_mail(receiver, payload):
    sender = f"{MAIL['name']} <{MAIL['email']}>"

    message = MIMEMultipart('alternative')
    message['Message-ID'] = make_msgid()
    message['Subject'] = 'Verifizierung'
    message['From'] = sender
    message['To'] = receiver
    message['Date'] = str(datetime.now())

    with open(BASE_DIR.joinpath('templates', 'mail', 'verification.md')) as file:
        content = file.read()
        for key, value in payload.items():
            content = content.replace('${' + key + '}', value)

    text = content
    html = md.markdown(content, extensions=['fenced_code'])

    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(html, 'html'))

    with smtplib.SMTP(MAIL['host'], MAIL['port']) as server:
        server.starttls()
        server.login(MAIL['username'], MAIL['password'])
        server.sendmail(sender, receiver, message.as_string())
