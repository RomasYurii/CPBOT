import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import dotenv_values


def send_email(info_data_email):
    config = dotenv_values("config.env")
    server = config.get("SMTP_SERVER")
    user = config.get("USER")
    password = config.get("PASSWORD")

    text = info_data_email

    recipients = [config.get("RECIPIENTS")]
    sender = config.get("USER")
    subject = 'Звернення з ТГ боту'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender

    part_text = MIMEText(text, 'plain')

    msg.attach(part_text)

    mail = smtplib.SMTP_SSL(server)
    mail.login(user, password)
    mail.sendmail(sender, recipients, msg.as_string())
    mail.quit()
