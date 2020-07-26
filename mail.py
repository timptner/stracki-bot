import settings
import smtplib
import markdown as md
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid

sender = f"{settings.mail['name']} <{settings.mail['email']}>"


def replace_all(text, d):
    for key, value in d.items():
        text = text.replace('${' + key + '}', value)

    return text


def verification_mail(receiver, payload):
    message = MIMEMultipart('alternative')
    message['Message-ID'] = make_msgid()
    message['Subject'] = 'Verifizierung'
    message['From'] = sender
    message['To'] = receiver
    message['Date'] = str(datetime.now())

    with open(settings.BASE_DIR.joinpath('templates', 'mail', 'verification.md')) as file:
        content = replace_all(file.read(), payload)

    text = content
    html = md.markdown(content, extensions=['fenced_code'])

    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(html, 'html'))

    with smtplib.SMTP(settings.mail['host'], settings.mail['port']) as server:
        server.starttls()
        server.login(settings.mail['username'], settings.mail['password'])
        server.sendmail(sender, receiver, message.as_string())
