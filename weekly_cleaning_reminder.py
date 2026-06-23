from hogsboutils import mailer, read_contacts, read_schedule, weekly_clean_send
import numpy as np
import datetime


def mail_to_cleaners(fetch_sheets=False, send=False):
    mailer("callum.rollo94@gmail.com", "started-it")
    schedule, areas_se, areas_en = read_schedule(fetch_sheet=fetch_sheets)
    contacts = read_contacts(fetch_sheet=fetch_sheets)
    row_number = np.abs(schedule['send_date'] - datetime.datetime.now()).argmin()
    this_date = schedule.iloc[row_number]['date']
    weekly_clean_send(schedule, this_date, contacts, areas_se, areas_en, print_msg=True, send=send)
    mailer("callum.rollo94@gmail.com", "sent-it")


if __name__ == '__main__':
    mail_to_cleaners()
