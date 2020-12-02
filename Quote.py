
class Component:

    def __init__(self, name, sku, qty):
        self.name = name
        self.sku = sku
        self.qty = qty

    def __str__(self):
        return f'{self.name}\t{self.sku}\t{self.qty}'


class Product:

    def __init__(self):
        self.product_description = ''
        self.sku = ''
        self.qty = ''
        self.price_each = ''
        self.price_total = ''
        self.old_price_each = None
        self.special_price_expiration = None

    def populate(self, row):
        self.product_description = row.find('p', class_='hp-product-description').text.strip()
        self.sku = row.find('span', class_='sku-desc').text.strip().replace(' ', '').replace('\t', '').replace('\n\n', '\n')
        self.qty = row.find('p', class_='item-quantity').text.strip()
        discount = row.find('div', class_='price hp-price price-content').find('s')
        if bool(discount):  # checks if the row has discounted price data to populate
            price_info_list = row.find('div', class_='price hp-price price-content').text.strip().replace('\t', '').replace('\n\n', '\n').split('\n')
            self.price_each = price_info_list[0]
            self.old_price_each = price_info_list[1]
            self.special_price_expiration = price_info_list[2]
        else:
            self.price_each = row.find(class_='price hp-price price-content').text.strip()
        self.price_total = row.find('span', class_='price').text.strip()

    def __str__(self):
        return f'Product Description: {self.product_description}\n{self.sku}\nQuantity: {self.qty}\nPrice Each: ' \
            f'{self.price_each}\nOld Price Each: {self.old_price_each}\nPrice Each Expiration: ' \
            f'{self.special_price_expiration}\nPrice Total: {self.price_total}\n'


class ConfigurableProduct(Product):

    def __init__(self):
        super().__init__()
        # self.reference_model = reference_model
        # self.configuration_id = configuration_id
        self.list_of_components = []

    def populate(self, row):
        super().populate(row)
        component_rows = row.tbody.findChildren('tr')
        for r in component_rows:
            name_sku_list = r.find('td', class_='component-name').text.strip().replace('\t', '').split('\n')
            name = name_sku_list[0]
            sku = name_sku_list[1]
            qty = r.find('td', class_='quantity').text.strip()
            component_obj = Component(name, sku, qty)
            self.list_of_components.append(component_obj)

    def __str__(self):
        components_string = ''
        for c in self.list_of_components:
            components_string += str(c) + '\n'
        return components_string

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
