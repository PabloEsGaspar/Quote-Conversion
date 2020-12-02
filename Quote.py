from Product import Product, ConfigurableProduct


class Quote:

    def __init__(self):
        self.quote_name = ''
        self.quote_number = ''
        self.purchaser_email = ''
        self.purchaser_name = ''
        self.purchaser_phone = ''
        self.created_by = ''
        self.date_created = ''
        self.expiration_date = ''
        self.subtotal = ''
        self.quote_total = ''
        self.contract_name = ''
        self.special_pricing_code = ''
        self.list_of_products = []

    def populate(self, soup):
        """calls several methods to divide the work of scraping the html and populating the Quote attributes"""
        self.populate_numbers(soup)
        self.populate_purchaser_info(soup)
        self.populate_names(soup)
        self.populate_dates(soup)
        self.populate_special_code(soup)
        self.populate_list_of_products(soup)

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
            if bool(configurable_tag):  # check if data has sub components
                product_object = ConfigurableProduct()
            else:
                product_object = Product()
            product_object.populate(row)
            self.list_of_products.append(product_object)

    def populate_special_code(self, soup):
        try:
            self.special_pricing_code = soup.find('div', id='total_breakdown').find('div', class_='left').find('div') \
                .find_next_sibling('div').text.strip()
        except AttributeError:
            print('no special pricing code found in HTML')
            self.special_pricing_code = None

    def populate_dates(self, soup):
        self.date_created = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform').find_next_sibling \
            ('div', class_='col6 ccol6 orderform').find('div', class_='form-2col order-inputs').find_next_sibling \
            ('div', class_='form-2col order-inputs').find('span').text.strip()
        self.expiration_date = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform').find_next_sibling \
            ('div', class_='col6 ccol6 orderform').find('div', class_='form-2col order-inputs').find_next_sibling \
            ('div', class_='form-2col order-inputs').find_next_sibling('div', class_='form-2col order-inputs') \
            .find('span').text.strip()

    def populate_names(self, soup):
        self.quote_name = soup.find('h1', class_='quote-header quote-bold-header').text.strip()
        self.created_by = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform') \
            .find('div', class_='form-2col order-inputs created-by').find('span').text.strip()
        self.contract_name = soup.find('div', class_='contract').find('p', class_='company-view').text.strip()

    def populate_numbers(self, soup):
        self.quote_number = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform').find_next_sibling \
        ('div', class_='col6 ccol6 orderform').find('div', class_='form-2col order-inputs').find('span').text.strip()
        self.subtotal = soup.find('div', id='total_breakdown').find('td', class_='total_figures').text.strip()
        self.quote_total = soup.find("div", class_='grey-bg').find('div', class_='col6 ccol6 orderform') \
            .find('div', class_='form-2col order-inputs').find_next_sibling('div', class_='form-2col order-inputs') \
            .find('span').text.strip()

    def populate_purchaser_info(self, soup):
        purchaser_info = soup.find(class_='combined-detail').text.strip()[:-1]
        purchaser_info_list = purchaser_info.split(', ')
        self.purchaser_name = purchaser_info_list[0]
        self.purchaser_email = purchaser_info_list[1]
        self.purchaser_phone = purchaser_info_list[2]

    def __str__(self):
        product_string = ''
        for p in self.list_of_products:
            product_string += str(p) + '\n'
        if self.special_pricing_code is None:
            special_pricing_code_string = ''
        else:
            special_pricing_code_string = f'Special Pricing Code: {self.special_pricing_code}'
        return f'\nQuote Name: {self.quote_name}\nQuote Number: {self.quote_number}\nPurchaser Name: {self.purchaser_name}' \
               f'\nPurchaser Email: {self.purchaser_email}\nPurchaser Phone: {self.purchaser_phone}\nCreated By: ' \
               f'{self.created_by}\nDate Created: {self.date_created}\nExpiration Date: {self.expiration_date}\n' \
               f'Subtotal: {self.subtotal}\nQuote Total: {self.quote_total}\nContract Name: {self.contract_name}\n' + \
               special_pricing_code_string + '\n\n' + product_string
