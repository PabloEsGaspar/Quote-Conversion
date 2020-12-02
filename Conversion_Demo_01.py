import imaplib
import email
import os
from Quote import Quote
from bs4 import BeautifulSoup
import codecs
import smtplib
from email.message import EmailMessage
import time
import json
import pdfkit


user = 'quote.conversion@gmail.com'
password = '@kodama14'
imap_url = 'imap.gmail.com'
attachment_dir = 'attachment_dir'
sleep_time = 30  # seconds between each iteration of the program/how frequently the program checks for new emails


def send_email(receiver_email, quote_object):
    """
    Creates an EmailMessage object and adds all quote data to the body. Uses an smtp mail server to send email
    to given address.
    :param receiver_email:
    :param quote_object:
    :return: None
    """
    msg = EmailMessage()
    msg['Subject'] = 'Quote Conversion Response - Kodama Group'
    msg['From'] = user
    msg['To'] = receiver_email

    json_quote = json.dumps(quote_object.__dict__, default=lambda o: o.__dict__, indent=4)
    msg.set_content(f'See JSON string of the quote data below: \n{json_quote}\n\n\nKodama Group\nQuote Conversion Demo')
    # ^sets the body of the email
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # used pdfkit library to generate a pdf
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    string_quote_data = str(quote_object)
    pdfkit.from_string(string_quote_data, 'out.pdf', configuration=config)

    with open('out.pdf', 'rb') as f:  # adds attachment
        file_data = f.read()
        file_name = f.name
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()  # identifies ourselves w/ mail server
        smtp.starttls()  # encrypts traffic
        smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)
    os.remove('out.pdf')  # deletes pdf file from project directory


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
            file_path = os.path.join(attachment_dir, file_name)
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


if __name__ == "__main__":  # MAIN METHOD
    con = auth(user, password, imap_url)  # open connection with imap server

    while True:  # endless loop to keep checking inbox for new mail
        typ, data = con.select('INBOX')  # set mailbox to INBOX
        num_emails = int(data[0])  # get total number of emails in inbox
        for i in range(1, num_emails + 1):  # loop through emails in inbox
            b_string = bytes(str(i), encoding="ascii")  # creates str b'i' / b'1' = the oldest email in the mailbox
            print(f'Loop #{i}... b_string = {b_string}')
            result, data = con.fetch(b_string, '(RFC822)')  # fetch email data
            email_msg = email.message_from_bytes(data[0][1])  # decode email data
            if email_has_attachment(email_msg):  # check if email has an html attachment
                html_file_path = get_attachments(email_msg)  # store html attachment in attachment_dir folder
                return_email_address = email_msg.get('FROM')  # save the email's 'from' address tp variable
                quote_obj = generate_quote_object(html_file_path)  # use html to create quote object
                send_email(return_email_address, quote_obj)  # send response email
                os.remove(html_file_path)  # delete html file from attachment_dir now that it's no longer needed
            print(f"deleting email b'{i}'")
            # con.store(b_string, '+FLAGS', r'(\Deleted)')  # delete email from inbox
        print(f'sleeping for {sleep_time} seconds')
        time.sleep(sleep_time)  # wait 30 sec before beginning new iteration of while loop

