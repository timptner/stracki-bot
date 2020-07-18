from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from helpers import replace_all
from markdown import markdown
from settings import MAIL_NAME, MAIL_EMAIL, MAIL_HOST, MAIL_PORT, MAIL_USER, MAIL_PASS
from smtplib import SMTP

sender = f'{MAIL_NAME} <{MAIL_EMAIL}>'


def verification_mail(receiver, payload):
    message = MIMEMultipart('alternative')
    message['Message-ID'] = make_msgid()
    message['Subject'] = 'Verifizierung'
    message['From'] = sender
    message['To'] = receiver
    message['Date'] = str(datetime.now())

    with open('templates/mail/verification.md') as file:
        content = replace_all(file.read(), payload)

    text = content
    html = markdown(content)

    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(html, 'html'))

    with SMTP(MAIL_HOST, MAIL_PORT) as server:
        server.starttls()
        server.login(MAIL_USER, MAIL_PASS)
        server.sendmail(sender, receiver, message.as_string())
