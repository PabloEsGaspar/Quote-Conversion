
class Product:

    def __init__(self, product_description, qty='', price_each='', price_total=''):
        self.product_description = product_description
        self.qty = qty
        self.price_each = price_each
        self.price_total = price_total

    def __str__(self):
        return f'Product Description: {self.product_description}\nQuantity: {self.qty}\nPrice Each: ' \
            f'{self.price_each}\nPrice Total: {self.price_total}\n'


class Quote:

    def __init__(self):
        self.quote_number = ''
        self.purchaser_name = ''
        self.purchaser_email = ''
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
        self.populate_numbers(soup)
        self.populate_purchaser_info(soup)
        self.populate_names(soup)
        self.populate_dates(soup)
        self.populate_special_code(soup)
        self.populate_list_of_products(soup)

    def populate_list_of_products(self, soup):
        product_descriptions = soup.find_all(class_='hp-product-description')  # scraping product info into resultSets
        product_quantities_set = soup.find_all(class_='item-quantity')
        price_each_set = soup.find_all(class_='price hp-price price-content')
        price_total_set = soup.find_all("span", class_='price')
        for i in range(len(product_descriptions)):  # loop through the resultSets to create a list of Products
            self.list_of_products.append(Product(product_descriptions[i].text.strip(), product_quantities_set[i].text.strip(),
                            price_each_set[i].text.strip().split('\n', 1)[0], price_total_set[i].text.strip()))

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
        return f'Quote Number: {self.quote_number}\nPurchaser Name: {self.purchaser_name}\nPurchaser Email: ' \
            f'{self.purchaser_email}\nPurchaser Phone: {self.purchaser_phone}\nCreated By: {self.created_by}\nDate ' \
            f'Created: {self.date_created}\nExpiration Date: {self.expiration_date}\nSubtotal: ' \
            f'{self.subtotal}\nQuote Total: {self.quote_total}\nContract Name: {self.contract_name}\n' + \
               special_pricing_code_string + '\n\n' + product_string





