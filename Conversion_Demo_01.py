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
from email.header import decode_header


logo_url = 'https://docamatic.s3-eu-west-1.amazonaws.com/assets/kodama.png'
user = 'quote.conversion@gmail.com'
password = 'qdyjwhkgsukfbwux'  # Gmail app password increases security, makes IMAP connection more reliable
imap_url = 'imap.gmail.com'
root_dir = '.'  # root dir path - where attachments are imported, scraped for data, and deleted
sleep_time = 45  # seconds between each iteration of the program/how often to check inbox for new mail


def send_connection_failure_email():
    msg = EmailMessage()
    msg['Subject'] = 'WARNING - Quote Conversion Failure'
    msg['From'] = user
    msg['To'] = 'gaspartonnesen@gmail.com'
    msg['Cc'] = 'josh@kodamagroup.com'
    msg.set_content(
        "WARNING\n\nQUOTE CONVERSION APP HAS SHUT DOWN DUE TO REPEATED FAILURES TO CONNECT TO GMAIL'S IMAP SERVER."
        "\n\nPLEASE SERVICE ASAP.")  # sets body
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()  # identifies ourselves w/ mail server
        smtp.starttls()  # encrypts traffic
        smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)


def send_conversion_failure_email(return_address, html_file_path, e):
    msg = EmailMessage()
    msg['Subject'] = 'WARNING - Quote Conversion Failure'
    msg['From'] = user
    # msg['To'] = 'gaspartonnesen@gmail.com'
    msg['To'] = 'quotes@kodamagroup.com'
    msg['Cc'] = 'gaspartonnesen@gmail.com'
    msg.set_content('WARNING\n\nQuote conversion app failed to convert html file <' + html_file_path + '> that was sent'
                    ' by ' + return_address + '.\n\nConversion Tool is still operational, but development is required '
                    'before this file can be processed.\n\nException: ' + str(e))
    # with open(html_file_path, 'rb') as f:
    #     file_data = f.read()
    #     file_name = f.name
    # msg.add_attachment(file_data, maintype='application', subtype='html', filename=file_name)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()  # identifies ourselves w/ mail server
        smtp.starttls()  # encrypts traffic
        smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)


def send_email(receiver_email, quote_object):
    """
    organizes quote data into a docamatic post request to send pdf to email provided
    :param receiver_email:
    :param quote_object:
    :return None:
    """
    headers_dict = {'Authorization': 'Bearer ctCMVLF6pNWrCxj9JZ3e7lEIUbCWAF6kPfyHqh0z',
                    'Content-Type': 'application/json'}
    json_body = create_json_data(receiver_email, quote_object)
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
    text_body = "Hello, this email is an automated response to a conversion request sent from " + receiver_email_substring + \
                ". The html file you provided has completed the conversion process and the resulting " \
                "pdf quote should be attached and accurate. If this is not the case please forward this email to " \
                "gaspartonnesen@gmail.com."
    # email_data = {'to': 'gaspartonnesen@gmail.com', 'filename': file_name,
    email_data = {'to': 'quotes@kodamagroup.com', 'filename': file_name,
                  'subject': quote_obj.quote_name + ' Quote Conversion Response - Do Not Reply', 'body': text_body}

    data_dict['data'] = data_body
    data_dict['email'] = email_data
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


def get_all_attachments(msg):
    """
    Saves the email attachment in the attachment_dir folder so that we can begin data scraping
    :param msg:
    :return file_path: (where the html file is now located)
    """
    html_file_paths = []
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_name = get_part_filename(part)
        if file_name.endswith('.html') and bool(file_name):
            file_path = os.path.join(root_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(part.get_payload(decode=True))
            html_file_paths.append(file_path)
    return html_file_paths


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
        file_name = get_part_filename(part)
        if not file_name.endswith('.html'):
            continue
        if file_name.endswith('.html'):
            return bool(file_name)
        else:
            return False
    return False


def get_part_filename(msg: EmailMessage):
    """
    decodes filename if necessary, otherwise just returns the regular filename
    :param msg:
    :return:
    """
    filename = msg.get_filename()
    if decode_header(filename)[0][1] is not None:
        filename = decode_header(filename)[0][0].decode(decode_header(filename)[0][1])
    return filename


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
        connection_failure_count = 0
        print(f'{get_timestamp_string()} | Successfully connected to IMAP Server - Mailbox accessible')
        typ, data = con.select('INBOX')  # set mailbox to INBOX
        typ, data = con.search(None, 'ALL')
        email_list = data[0].split()
        if len(email_list) == 0:
            print(f'{get_timestamp_string()} | No messages found - INBOX was empty')
        else:
            for num in data[0].split():  # loop through emails in inbox
                print(f'{get_timestamp_string()} | Began processing email #{num} from inbox')
                result, data = con.fetch(num, '(RFC822)')  # fetch email data
                email_msg = email.message_from_bytes(data[0][1])  # decode email data

                if email_has_attachment(email_msg):  # check if email has an html attachment

                    return_email_address = email_msg.get('FROM')  # save the email's 'from' address
                    list_of_html_file_paths = get_all_attachments(email_msg)  # store html attachment in attachment_dir folder
                    print(f'{get_timestamp_string()} | consumed email attachment(s) sent from {return_email_address}')

                    for html_file_path in list_of_html_file_paths:
                        file_number = list_of_html_file_paths.index(html_file_path) + 1
                        try:
                            quote_obj = generate_quote_object(html_file_path)  # use html to create quote object
                        except Exception as e:
                            print(f'{get_timestamp_string()} | FAILED TO CONVERT ATTACHMENT #{file_number} - HTML file: {html_file_path}')
                            print(f'{get_timestamp_string()} | Conversion Error: {(str(e.args[0])).encode("utf-8")}')
                            send_conversion_failure_email(return_email_address, html_file_path, e)
                        else:
                            print(f"{get_timestamp_string()} | Successfully converted file #{file_number}")
                            send_email(return_email_address, quote_obj)  # send response email through Docamatic
                        finally:
                            os.remove(html_file_path)  # delete html file from attachment_dir now that it's no longer needed
                else:
                    print(f'{get_timestamp_string()} | Email had no attachments')

                print(f"{get_timestamp_string()} | deleting email #{num} from inbox")
                con.store(num, '+FLAGS', r'(\Deleted)')  # delete email from inbox
        con.expunge()
        print(f'{get_timestamp_string()} | closing IMAP connection - Killed mailbox access ')
        print(f'{get_timestamp_string()} | sleeping for {sleep_time} seconds\n'
              f'------------------------------------------------------------------------------------------------------')
        con.logout()
        time.sleep(sleep_time)

    print(f'{get_timestamp_string()} | APPLICATION TERMINATING DUE TO REPEATED FAILURE TO CONNECT TO IMAP SERVER...')


# git push heroku main   push to remote cloud repo
# heroku                 display list of commands
# heroku logs --tail     live feed of console while program runs
# Quote Conversion
