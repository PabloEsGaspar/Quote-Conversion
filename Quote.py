from Product import Product, ConfigurableProduct, DiscountConfigurableProduct, DiscountProduct


class PurchasingInfo:

    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value


class Quote:

    def __init__(self):
        self.color = '#2C5E41'
        self.accent_color = '#FFF3AF'
        self.company = {'logo': 'https://docamatic.s3-eu-west-1.amazonaws.com/assets/kodama.png'}
        self.title = 'HP OFFICIAL QUOTE'
        self.subtitle = 'This quote is HP/Kodama Group Confidential and Proprietary Information. Do not share.'
        self.quote_name = ''
        self.quote_number = ''
        self.quote_date = ''
        self.quote_expiration = ''
        self.account_rep = 'Josh Miles'
        self.phone = '720.617.0951'
        self.email = 'quotes@kodamagroup.com'
        self.notes = 'Please contact sales'
        self.special_pricing_code = ''
        self.purchasing_information = []
        self.lines = []
        self.subtotal = ''
        self.total = ''
        self.terms_and_conditions = ['The terms and conditions of the CO - STATE OF COLORADO (NASPO VP PC) '
                                     '[2016000000000142NASPO] contract will apply to any order placed as a result of '
                                     'this inquiry, no other terms or conditions shall apply.',
                                     'HP and/or Kodama Group, LLC are not liable for pricing errors. '
                                     'If you place an order for a product that was incorrectly priced, '
                                     'we will cancel your order and credit you for any charges. '
                                     'In the event that we inadvertently ship an order based on a pricing error, '
                                     'we will issue a revised invoice to you for the correct price and contact you to '
                                     'obtain your authorization for the additional charge, or assist you with return '
                                     'of the product. If the pricing error results in an overcharge to you, HP will '
                                     'credit your account for the amount overcharged.', 'Freight is FOB Destination.']
        self.custom_tables = [{'head': 'HP Inc. Vendor Address', 'body': 'The HP, Inc. Vendor address is:\n\nHP Inc.'
                               '\nAttn: Public Sector Sales\n3800 Quick Hill Road\nBldg 2, Suite 100'
                                                                         '\nAustin, TX 78728'}]

    def populate(self, soup):
        """calls several methods to divide the work of scraping the html and populating the Quote attributes"""
        self.populate_numbers(soup)
        self.populate_names(soup)
        self.populate_dates(soup)
        self.populate_special_code(soup)
        self.populate_purchasing_information(soup)
        self.populate_list_of_products(soup)

    def populate_purchasing_information(self, soup):
        purchase_info_01 = PurchasingInfo('HP Quote Number', self.quote_number)
        purchase_info_02 = PurchasingInfo('Contract Name', soup.find('div', class_='contract')
                                          .find('p', class_='company-view').text.strip())
        purchase_info_03 = PurchasingInfo('Purchasing Instructions',
                                          'Please make PO out to HP Inc, list Partner ID: 991000721949 and Quote ID:'
                                          ' 1594087 on PO. Forward PO to orders@kodamagroup.com for processing. '
                                          'Do not send to HP. Thank you!')
        self.purchasing_information.append(purchase_info_01)
        self.purchasing_information.append(purchase_info_02)
        self.purchasing_information.append(purchase_info_03)

    def populate_list_of_products(self, soup):
        """
        scrapes html data for a list of products, iteratively creates product objects,
        and appends them to Quote's list_of_products
        :param soup:
        :return none:
        """
        product_rows = soup.find(id='order_details').tbody.findChildren('tr', attrs={'class': None}, recursive=False)
        for row in product_rows:
            configurable_tag = row.find('div', class_='kit-detail-component')
            discount = row.find('div', class_='price hp-price price-content').find('s')
            if bool(configurable_tag):  # check if data has sub components
                if bool(discount):  # checks if the row has discounted price data to populate
                    product_object = DiscountConfigurableProduct()
                else:
                    product_object = ConfigurableProduct()
            else:
                if bool(discount):  # checks if the row has discounted price data to populate
                    product_object = DiscountProduct()
                else:
                    product_object = Product()
            product_object.populate(row)
            self.lines.append(product_object)

    def populate_special_code(self, soup):
        try:
            self.special_pricing_code = soup.find('div', id='total_breakdown').find('div', class_='left').find('div') \
                .find_next_sibling('div').text.strip()
        except AttributeError:
            print('no special pricing code found in HTML')
            self.special_pricing_code = None

    def populate_dates(self, soup):
        self.quote_date = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform').find_next_sibling \
            ('div', class_='col6 ccol6 orderform').find('div', class_='form-2col order-inputs').find_next_sibling \
            ('div', class_='form-2col order-inputs').find('span').text.strip()
        self.quote_expiration = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform').find_next_sibling \
            ('div', class_='col6 ccol6 orderform').find('div', class_='form-2col order-inputs').find_next_sibling \
            ('div', class_='form-2col order-inputs').find_next_sibling('div', class_='form-2col order-inputs') \
            .find('span').text.strip()

    def populate_names(self, soup):
        self.quote_name = soup.find('h1', class_='quote-header quote-bold-header').text.strip()

    def populate_numbers(self, soup):
        self.quote_number = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform').find_next_sibling \
        ('div', class_='col6 ccol6 orderform').find('div', class_='form-2col order-inputs').find('span').text.strip()
        self.subtotal = soup.find('div', id='total_breakdown').find('td', class_='total_figures').text.strip()
        self.total = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform') \
            .find('div', class_='form-2col order-inputs').find_next_sibling('div', class_='form-2col order-inputs') \
            .find('span').text.strip()

    def __str__(self):
        product_string = ''
        for p in self.lines:
            product_string += str(p) + '\n'
        if self.special_pricing_code is None:
            special_pricing_code_string = ''
        else:
            special_pricing_code_string = f'Special Pricing Code: {self.special_pricing_code}'
        return f'\nQuote Name: {self.quote_name}\nQuote Number: {self.quote_number}' \
               f'\nDate Created: {self.quote_date}\nExpiration Date: {self.quote_expiration}\n' \
               f'Subtotal: {self.subtotal}\nQuote Total: {self.total}\nContract Name: missing code retrieve contract name\n' + \
               special_pricing_code_string + '\n\n' + product_string

