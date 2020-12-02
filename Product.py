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
        self.sku = row.find('span', class_='sku-desc').text.strip().replace(' ', '').replace('\t', '').replace('\n\n',
                                                                                                               '\n')
        self.qty = row.find('p', class_='item-quantity').text.strip()
        discount = row.find('div', class_='price hp-price price-content').find('s')
        if bool(discount):  # checks if the row has discounted price data to populate
            price_info_list = row.find('div', class_='price hp-price price-content').text.strip().replace('\t',
                                                                                                          '').replace(
                '\n\n', '\n').split('\n')
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
