import imaplib, email, os
from Quote import Quote, Product
from bs4 import BeautifulSoup
import codecs
import smtplib
from email.message import EmailMessage
import time
import json
import pdfkit


user = 'gtonnesen14@gmail.com'
password = 'nobilityis'
imap_url = 'imap.gmail.com'
attachment_dir = 'attachment_dir'


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
    msg.set_content(f'See JSON string of the quote data below: \n{json_quote}\n\n\nKodama Group\nQuote Conversion Demo')  # sets body

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
    os.remove('out.pdf')


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
            # print('part.getcontentmaintyhpe = multipart')
            continue
        if part.get('Content-Disposition') is None:
            # print('Content-Disposition is None')
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
    Scrapes quote data from html file at given filepath, then instantiates a quote object with the data from the html
    :param file_path:
    :return: Quote object
    """
    f = codecs.open(file_path, 'r')  # stores html in a string variable
    html_data = f.read()
    soup = BeautifulSoup(html_data, 'html.parser')  # scrape html for quote info and use it to make a quote object

    quote_number = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform').find_next_sibling \
        ('div', class_='col6 ccol6 orderform').find('div', class_='form-2col order-inputs').find('span').text.strip()
    purchaser_info = soup.find(class_='combined-detail').text.strip()
    purchaser_info = purchaser_info[:-1]  # removes last character of string which is a ',' in this case
    purchaser_info_list = purchaser_info.split(', ')
    purchaser_name = purchaser_info_list[0]
    purchaser_email = purchaser_info_list[1]
    purchaser_phone = purchaser_info_list[2]
    created_by = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform') \
        .find('div', class_='form-2col order-inputs created-by').find('span').text.strip()
    date_created = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform').find_next_sibling \
        ('div', class_='col6 ccol6 orderform').find('div', class_='form-2col order-inputs').find_next_sibling \
        ('div', class_='form-2col order-inputs').find('span').text.strip()
    expiration_date = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform').find_next_sibling \
        ('div', class_='col6 ccol6 orderform').find('div', class_='form-2col order-inputs').find_next_sibling \
        ('div', class_='form-2col order-inputs').find_next_sibling('div', class_='form-2col order-inputs') \
        .find('span').text.strip()
    special_pricing_code = soup.find('div', id='total_breakdown').find('div', class_='left').find('div') \
        .find_next_sibling('div').text.strip()
    subtotal = soup.find('div', id='total_breakdown').find('td', class_='total_figures').text.strip()
    quote_total = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform') \
        .find('div', class_='form-2col order-inputs').find_next_sibling('div', class_='form-2col order-inputs') \
        .find('span').text.strip()
    contract_name = soup.find('div', class_='contract').find('p', class_='company-view').text.strip()

    quote_object = Quote(quote_number, purchaser_name, purchaser_email, purchaser_phone, created_by, date_created,
                         expiration_date, special_pricing_code, subtotal, quote_total, contract_name,
                         generate_list_of_products(soup))

    return quote_object


def generate_list_of_products(soup):
    """
    uses soup parser provided to scrape the html, then uses the data to create a list of Product objects
    :param soup:
    :return List[Products]:
    """
    product_descriptions = soup.find_all(class_='hp-product-description')  # scraping product info into resultSets
    product_quantities_set = soup.find_all(class_='item-quantity')
    price_each_set = soup.find_all(class_='price hp-price price-content')
    price_total_set = soup.find_all("span", class_='price')
    count = 0
    my_products = []
    for p in product_descriptions:  # loop through the resultSets to create a list of Products
        my_products.append(Product(p.text.strip(), product_quantities_set[count].text.strip(),
                                   price_each_set[count].text.strip().split('\n', 1)[0],
                                   price_total_set[count].text.strip()))
        count += 1
    return my_products


if __name__ == "__main__":  # MAIN METHOD

    con = auth(user, password, imap_url)  # open connection with imap server

    while True:  # endless loop to keep checking inbox for new mail
        typ, data = con.select('INBOX')  # set mailbox to INBOX
        num_emails = int(data[0])  # get total number of emails in inbox

        for i in range(1, num_emails + 1):  # loop thru each email in the inbox
            b_string = bytes(str(i), encoding="ascii")  # creates str b'i' / b'1' = the oldest email in the mailbox
            print(f'Loop #{i}... b_string = {b_string}')
            result, data = con.fetch(b_string, '(RFC822)')  # fetch email data
            email_msg = email.message_from_bytes(data[0][1])  # decode email

            if email_has_attachment(email_msg):  # check email for attachment
                html_file_path = get_attachments(email_msg)  # store attachment in attachment_dir folder
                return_email_address = email_msg.get('FROM')
                quote_obj = generate_quote_object(html_file_path)

                send_email(return_email_address, quote_obj)

            print(f"deleting email b'{i}'")
            con.store(b_string, '+FLAGS', r'(\Deleted)')  # deletes email from inbox

        sleep_time = 30
        print(f'sleeping for {sleep_time} seconds')
        time.sleep(sleep_time)  # wait 30 sec before beginning new iteration of while loop

