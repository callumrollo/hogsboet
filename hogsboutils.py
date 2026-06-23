import smtplib
from email.message import EmailMessage
import json
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

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
    
def read_contacts(fetch_sheet=False):
    contacts_csv = Path('contacts.csv')
    if fetch_sheet or not contacts_csv.exists():
        contacts = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{email_auth["contacts_sheet"]}/export?format=csv&gid=0#',
                       skiprows=3, )
        contacts = contacts[2:]
        contacts.to_csv(contacts_csv, index=False)
        return contacts
    else:
        contacts = pd.read_csv(contacts_csv)
        return contacts

def read_schedule(fetch_sheet=False):
    schedule_csv = Path('schedule.csv')
    if fetch_sheet or not schedule_csv.exists():
        df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{email_auth["schedule_sheet"]}/export?format=csv&gid=0#',
                           skiprows=3, names=['date', 'a1', 'a2', 'a3', 'a4'])
        df.to_csv(schedule_csv, index=False)

    else:
        df = pd.read_csv(schedule_csv)
    areas_se = df.iloc[0].to_dict()
    areas_en = df.iloc[1].to_dict()
    schedule = df[22:-1]
    dates = pd.date_range(start="2026-04-04", periods=len(schedule), freq="7D")
    schedule['send_date'] = dates
    return schedule, areas_se, areas_en



def cleaning_mail(responsible, recipient_email, area_code, areas_se, areas_en):
    area_se = areas_se[area_code].lower().replace('\n', '')
    area_en = areas_en[area_code].lower().replace('\n', '')

    msg = f"<English below> \n\n" \
          f"Hej {responsible.capitalize()}! 🧹🧽✨\n\n" \
          f"En vänlig påminnelse att det är din tur att städa {area_se} den har helgen. " \
          "Om du har frågor kan du kontakta Städgruppen på Discord, eller mejla Lotta på lotta_eklund@yahoo.se. Vänligen svara inte på detta mejl.\n\n" \
          "Med vänliga hälsingar\nStädgruppen och styrelsen.\n\n" \
          f"Hi {responsible.capitalize()}! 🧹🧽✨\n\n" \
          f"A friendly reminder that it is your turn to clean the {area_en} this weekend. " \
          "If you have any questions, kindly contact the cleaning group on Discord, or Lotta at lotta_eklund@yahoo.se. Please do not reply to this email.\n\n" \
          "Kind regards\nCleaning group & board.\n\n"
    mailer(recipient_email, msg)
    
def weekly_clean_send(df, week, contacts, areas_se, areas_en, send=False, print_msg=True):
    cleaners = df[df.date==week][['a1', 'a2', 'a3', 'a4']].iloc[0].to_dict()
    for area, cleaner in cleaners.items():
        if area =='date':
            continue
        cleaner_row = contacts[contacts['Cleaning name'] == cleaner]
        if len(cleaner_row) == 0:
            print(f"FAIL! for {cleaner} not found in contacts sheet")
            continue
        if len(cleaner_row) > 1:
            if '&' not in cleaner:
                print(f"FAIL! Found unexpected multiple matches for {cleaner} {len(cleaner_row)}")
        for mail in cleaner_row['E-post / Email Address']:
            if send:
                cleaning_mail(cleaner, mail, area, areas_se, areas_en)
            if print_msg:
                print(week, cleaner, mail, areas_en[area])