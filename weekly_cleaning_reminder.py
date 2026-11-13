from hogsboutils import mailer, read_contacts, read_schedule, weekly_clean_send, weekly_cook_send
import numpy as np
import datetime


def mail_to_cleaners(fetch_sheets=True, send=False):
    mailer("callum.rollo94@gmail.com", "started-it")
    
    schedule, areas_se, areas_en = read_schedule("2026-09-04", fetch_sheet=fetch_sheets)
    contacts = read_contacts(fetch_sheet=fetch_sheets)
    row_number = np.abs(schedule['send_date'] - datetime.datetime.now()).argmin()
    this_date = schedule.iloc[row_number]['date']
    weekly_clean_send(schedule, this_date, contacts, areas_se, areas_en, print_msg=True, send=send)

    cooking_schedule = read_cooking_schedule(fetch_sheet=True)
    cooking_send_dict = cooking_schedule[cooking_schedule['week']==next_week].dropna(axis=1).iloc[0].to_dict()
    this_week = datetime.datetime.now().isocalendar()[1]
    next_week = (this_week + 1) % 52
    weekly_cook_send(cooking_send_dict)
    weekly_cook_send(cook_dict, send=send)
    
    mailer("callum.rollo94@gmail.com", "sent-it")


if __name__ == '__main__':
    mail_to_cleaners()
