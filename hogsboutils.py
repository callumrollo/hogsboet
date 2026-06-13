import random
import copy
import smtplib
from email.message import EmailMessage
import json

with open("email_auth.json") as f:
    # Read in the auth for your mail account (tested with gmail app password only)
    email_auth = json.load(f)
    gmail_username = email_auth['gmail_username']
    gmail_app_password = email_auth['gmail_app_password']

def mailer(recipient, message, sender="noreply Högsboet bot", subject="Städpåminnelse / Cleaning reminder"):
    """
    Utility script for sending emails. You shouldn't need to change anything here
    :param recipient: email recipient
    :param message: email message
    :param sender: sender name
    :param subject: email subject
    :return: None
    """
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    server = smtplib.SMTP('smtp.gmail.com', 25)
    server.connect('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(gmail_username, gmail_app_password)
    server.send_message(msg)
    server.quit()