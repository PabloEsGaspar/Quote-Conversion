import imaplib
import email
import os
from Quote import Quote
from bs4 import BeautifulSoup
import codecs
import time
import json
import requests
import re
import smtplib
from email.message import EmailMessage
from datetime import datetime


# global variables
logo_url = 'https://docamatic.s3-eu-west-1.amazonaws.com/assets/kodama.png'
user = 'quote.conversion@gmail.com'
password = 'qdyjwhkgsukfbwux'  # Gmail app password increases security, makes IMAP connection more reliable
imap_url = 'imap.gmail.com'
root_dir = '.'  # root dir path - where attachments are imported, scraped for data, and deleted
sleep_time = 30  # seconds between each iteration of the program/how often to check inbox for new mail


def send_email(receiver_email, quote_object):
    """
    organizes quote data into a docamatic post request to send pdf to email provided
    :param receiver_email:
    :param quote_object:
    :return None:
    """
    headers_dict = {'Authorization': 'Bearer ctCMVLF6pNWrCxj9JZ3e7lEIUbCWAF6kPfyHqh0z', 'Content-Type': 'application/json'}
    # below code was for image manipulation for providing our own logo but ended up not needing
    # img = Image.open(urlopen(logo_url))
    # big_img = img.resize((1856, 307))  # x 116%
    # big_img.save('kodama_logo_116%.png', 'PNG')
    # quote_object.company['logo'] = open('kodama_logo_116%.png', 'rb').read()
    json_body = create_json_data(receiver_email, quote_object)
    # print(json.dumps(data, indent=4))
    # print(f'valid json data: {is_json_valid(data)}')  # data param can't be a json string, must be dict, list, etc..
    response = requests.post('https://docamatic.com/api/v1/template', headers=headers_dict, json=json_body)
    print(f'{get_timestamp_string()} | response code from Docamatic: {response.status_code}')


def create_json_data(receiver_email, quote_object):
    """
    combines data into one big dictionary that is easily jsonifiable
    :param receiver_email:
    :param quote_object:
    :return data{}:
    """
    receiver_email_substring = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", receiver_email)[0]
    quote_name_str = f'Quote {quote_object.quote_number}'
    file_name = f'{quote_object.quote_number}-{quote_object.quote_name}'
    data_dict = {'template': 'quotation2', 'font': 'Calibri', 'font_size': 0.9, 'page_numbers': True,
                 'name': quote_name_str}
    data_body = quote_object.__dict__
    email_data = {'to': receiver_email_substring, 'filename': file_name, 'subject': 'Quote Conversion Response - Do Not Reply'}
    data_dict['data'] = data_body
    data_dict['email'] = email_data
    # print(f'data to json.dumps: {data_dict}')
    json_data = json.dumps(data_dict, default=lambda o: o.__dict__, indent=4)
    print(f'{get_timestamp_string()} | created body of Docamatic request for quote {file_name}')
    data = json.loads(json_data)
    return data


def is_json_valid(json_data):
    """
    return true if input is a valid json object and false otherwise
    :param json_data:
    :return boolean:
    """
    try:
        json.loads(json_data)
    except ValueError as err:
        return False
    return True


def auth(user, password, imap_url):
    """
    Creates imap connection with the gmail account given
    :param user:
    :param password:
    :param imap_url:
    :return: connection object
    """
    connection = imaplib.IMAP4_SSL(imap_url)
    connection.login(user, password)
    return connection


def get_attachments(msg):
    """
    Saves the email attachment in the attachment_dir folder so that we can begin data scraping
    :param msg:
    :return file_path: (where the html file is now located)
    """
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_name = part.get_filename()
        if bool(file_name):
            file_path = os.path.join(root_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(part.get_payload(decode=True))
            return file_path


def email_has_attachment(msg):
    """
    returns true if given email has an html attachment, false otherwise
    :param msg:
    :return boolean:
    """
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_name = part.get_filename()
        if file_name.endswith('.html'):
            return bool(file_name)
        else:
            return False


def generate_quote_object(file_path):
    """
    creates html parser 'soup' and a quote_object, then has the quote_object populate itself using 'soup'
    :param file_path:
    :return: Quote object
    """
    f = codecs.open(file_path, 'r')  # stores html in a string variable
    html_data = f.read()
    soup = BeautifulSoup(html_data, 'html5lib')  # scrape html for quote info and use it to make a quote object
    quote_object = Quote()
    quote_object.populate(soup)
    return quote_object


def send_connection_failure_email():
    msg = EmailMessage()
    msg['Subject'] = 'WARNING - Quote Conversion Failure'
    msg['From'] = user
    msg['To'] = 'gaspartonnesen@gmail.com'
    # msg['Cc'] = 'josh@kodamagroup.com'
    msg.set_content(
        "WARNING\n\nQUOTE CONVERSION APP HAS SHUT DOWN DUE TO REPEATED FAILURES TO CONNECT TO GMAIL'S IMAP SERVER."
        "\n\nPLEASE SERVICE ASAP.")  # sets body
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()  # identifies ourselves w/ mail server
        smtp.starttls()  # encrypts traffic
        smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)


def send_conversion_failure_email(html_file_path):
    msg = EmailMessage()
    msg['Subject'] = 'WARNING - Quote Conversion Failure'
    msg['From'] = user
    msg['To'] = 'gaspartonnesen@gmail.com'
    # msg['Cc'] = 'josh@kodamagroup.com'
    msg.set_content('WARNING\n\nQuote conversion app failed to convert the attached html file.\n\nApp is still '
                    'operational, but development is required before this file can be processed.')

    with open(html_file_path, 'rb') as f:
        file_data = f.read()
        file_name = f.name
        msg.add_attachment(file_data, maintype='application', subtype='html', filename=file_name)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()  # identifies ourselves w/ mail server
        smtp.starttls()  # encrypts traffic
        smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)


def get_timestamp_string():
    return datetime.now().strftime("%d/%m/%y - %I:%M:%S %p")


if __name__ == "__main__":  # MAIN METHOD
    connection_failure_count = 0
    while True:  # endless loop to keep checking inbox for new mail
        try:
            con = auth(user, password, imap_url)  # open connection with imap server
        except:
            print(f'{get_timestamp_string()} | IMAP CONNECTION FAILED\nsending email notification of failure')
            connection_failure_count += 1
            if connection_failure_count >= 3:
                send_connection_failure_email()
                break
        else:
            connection_failure_count = 0
            print(f'{get_timestamp_string()} | IMAP connection made')
            typ, data = con.select('INBOX')  # set mailbox to INBOX
            num_emails = int(data[0])  # get total number of emails in inbox
            if num_emails == 0:
                print(f'{get_timestamp_string()} | Inbox was empty')
            for i in range(1, num_emails + 1):  # loop through emails in inbox
                b_string = bytes(str(i), encoding="ascii")  # creates str b'i' / b'1' = the oldest email in the mailbox
                print(f'{get_timestamp_string()} | Processing email #{i} from inbox')
                result, data = con.fetch(b_string, '(RFC822)')  # fetch email data
                email_msg = email.message_from_bytes(data[0][1])  # decode email data
                if email_has_attachment(email_msg):  # check if email has an html attachment
                    html_file_path = get_attachments(email_msg)  # store html attachment in attachment_dir folder
                    return_email_address = email_msg.get('FROM')  # save the email's 'from' address to variable
                    try:
                        quote_obj = generate_quote_object(html_file_path)  # use html to create quote object
                    except:
                        print(f'{get_timestamp_string()} | FAILED TO CONVERT HTML FILE\nsending email notification of '
                              f'failure')
                        send_conversion_failure_email(html_file_path)
                    else:
                        send_email(return_email_address, quote_obj)  # send response email
                    os.remove(html_file_path)  # delete html file from attachment_dir now that it's no longer needed
                else:
                    print(f'{get_timestamp_string()} | Email had no attachment')
                print(f"{get_timestamp_string()} | deleting email #{i} from inbox")
                con.store(b_string, '+FLAGS', r'(\Deleted)')  # delete email from inbox

            print(f'{get_timestamp_string()} | closing IMAP connection | sleeping for {sleep_time} seconds')
            con.logout()
            time.sleep(sleep_time)

    print(f'{get_timestamp_string()} | APPLICATION TERMINATING DUE TO REPEATED FAILURE...')


# git push heroku main   push to remote cloud repo
# heroku                 display list of commands
# heroku logs --tail     live feed of console while program runs
