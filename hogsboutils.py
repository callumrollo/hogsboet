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

def read_cooking_schedule(fetch_sheet=False):
    cooking_csv = Path('cooking_schedule.csv')
    if fetch_sheet or not cooking_csv.exists():
        cooking = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{email_auth["cooking_schedule_sheet"]}/export?format=csv&gid=0#', header=2)
        cooking.to_csv(cooking_csv, index=False)
        return cooking
    else:
        cooking = pd.read_csv(cooking_csv)
        return cooking

def read_schedule(first_send, fetch_sheet=True):
    schedule_csv = Path('schedule.csv')
    if fetch_sheet or not schedule_csv.exists():
        df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{email_auth["schedule_sheet"]}/export?format=csv&gid={email_auth["schedule_sheet_gid"]}#',
                           skiprows=3, names=['date', 'a1', 'a2', 'a3', 'a4'])
        df.to_csv(schedule_csv, index=False)

    else:
        df = pd.read_csv(schedule_csv)
    areas_se = df.iloc[0].to_dict()
    areas_en = df.iloc[1].to_dict()
    schedule = df[20:]
    dates = pd.date_range(start=first_send, periods=len(schedule), freq="7D")
    schedule['send_date'] = dates
    for colname in ['a1', 'a2', 'a3', 'a4']:
        schedule[colname] = schedule[colname].str.rstrip()
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


def weekly_cook_send(send_dict, send=False, print_msg=True):
    team = [val for key, val in send_dict.items() if 'member' in key or key=='team lead']
    leader = send_dict['team lead']
    contacts_dict = {}
    for member in team:
        cleaner_row = contacts[contacts['Cleaning name'] == member]
        if len(cleaner_row)==0:
            print(f"FAIL for {member}")
            continue
        
        contacts_dict[member] = cleaner_row['E-post / Email Address'].values[0]
    channel = send_dict['discord-channel']
    swap = 'https://discord.com/channels/1126552312488394762/1515758459499577456'
    for member in team:
        leader_msg = ""
        if member == leader:
            leader_msg = f"Hi {member.capitalize()}!\n\nThank you for leading the cooking team this week. An automated reminder with the following text has just been sent to the following members of your team:{[name for key, name in send_dict.items() if 'member' in key]}. If that list does not match your expectations, please contact Callum on discord. Thanks!\n\n"
        msg_en = f"Hi {member.capitalize()}, \n\n" \
          f"A friendly reminder that you are on the cooking team next week! " \
          f"Please join the discussion on discord in channel {channel}. " \
          f"If you are unable to complete your cooking duties next week please make sure to find somone to switch with as soon as possible using the swap-duties channel {swap} and let your team know on discord or contact your team lead {leader.capitalize()} {contacts_dict[leader]} by 10 pm tomorrow. Please do not reply to this email.\n\n" \
          "Kind regards\nCooking group & board.\n\n"
        msg_se = f"Hej {member.capitalize()}, \n\n" \
        f"Här kommer en vänlig påminnelse om att du ingår i matlagningsgruppen nästa vecka! Var vänlig och delta i diskussionen på Discord "\
        f"i kanalen ⁠{channel}. Om du inte har möjlighet att delta nästa vecka, se till att hitta någon att byta med "\
        f"så snart som möjligt via kanalen för byte av uppgifter {swap} och meddela din matlagningsgrupp på Discord eller kontakta den sammankallande för gruppen "\
        f"{leader.capitalize()} {contacts_dict[leader]} senast kl. 22.00 imorgon. Svara inte på detta e-postmeddelande. "\
        "Med vänliga hälsningar\nMatlagningsgruppen och styrelsen."
        msg = f"{leader_msg}<English below>\n\n{msg_se}\n\n{msg_en}"
        cleaner_row = contacts[contacts['Cleaning name'] == member]
        email = cleaner_row['E-post / Email Address'].values[0]
        if print_msg:
            print(member, email)
            print(msg)
        
        if send:
            mailer(email, msg, sender="noreply Högsboet bot", subject="Cooking reminder / matlag påminnelse")

        
