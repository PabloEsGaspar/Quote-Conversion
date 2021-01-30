class Component:

    def __init__(self, name, sku):
        self.description = name
        self.sku = sku
        # self.quantity = qty

    def __str__(self):
        return f'{self.description}\t{self.sku}'


class Description:

    def __init__(self):
        self.title = ''
        self.subtitle = ''


class ConfigurableDescription(Description):

    def __init__(self):
        super().__init__()
        self.configuration = []


class Product:

    def __init__(self):
        self.description = Description()
        self.quantity = ''
        self.unit_price = ''
        self.total = ''

    def populate(self, row):
        self.description.title = row.find('p', class_='hp-product-description').text.strip()
        self.description.subtitle = row.find('span', class_='sku-desc').text.strip().replace(' ', '').replace('\t', '')\
            .replace('\n\n', '\n')
        self.quantity = row.find('p', class_='item-quantity').text.strip()
        self.unit_price = row.find(class_='price hp-price price-content').text.strip()
        self.total = row.find('span', class_='price').text.strip()

    def __str__(self):
        return f'Product Description: {self.description.title}\n{self.description.subtitle}\nQuantity: {self.quantity}' \
            f'\nPrice Each: {self.unit_price}\nPrice Total: {self.total}\n'


class DiscountProduct(Product):

    def __init__(self):
        super().__init__()
        self.original_unit_price = None
        self.special_price_valid_to = None

    def populate(self, row):
        self.description.title = row.find('p', class_='hp-product-description').text.strip()
        self.description.subtitle = row.find('span', class_='sku-desc').text.strip().replace(' ', '').replace('\t', '')\
            .replace('\n\n', '\n')
        self.quantity = row.find('p', class_='item-quantity').text.strip()
        price_info_list = row.find('div', class_='price hp-price price-content').text.strip().replace('\t',
                                                                                                      '').replace(
            '\n\n', '\n').split('\n')
        self.unit_price = price_info_list[0]
        self.original_unit_price = price_info_list[1]
        self.special_price_valid_to = price_info_list[2]
        self.total = row.find('span', class_='price').text.strip()

    def __str__(self):
        return f'Product Description: {self.description.title}\n{self.description.subtitle}\nQuantity: {self.quantity}\nPrice Each: ' \
            f'{self.unit_price}\nOld Price Each: {self.original_unit_price}\nPrice Each Expiration: ' \
            f'{self.special_price_valid_to}\nPrice Total: {self.total}\n'


class ConfigurableProduct(Product):

    def __init__(self):
        self.description = ConfigurableDescription()
        self.quantity = ''
        self.unit_price = ''
        self.total = ''

    def populate(self, row):
        super().populate(row)
        component_rows = row.tbody.findChildren('tr')
        for r in component_rows:
            name_sku_list = r.find('td', class_='component-name').text.strip().replace('\t', '').split('\n')
            name = name_sku_list[0]
            sku = name_sku_list[1]
            # qty = r.find('td', class_='quantity').text.strip()  # component qty removed
            component_obj = Component(name, sku)
            self.description.configuration.append(component_obj)

    def __str__(self):
        components_string = ''
        for c in self.description.configuration:
            components_string += str(c) + '\n'
        return components_string


class DiscountConfigurableProduct(DiscountProduct):

    def __init__(self):
        self.description = ConfigurableDescription()
        self.quantity = ''
        self.unit_price = ''
        self.original_unit_price = None
        self.special_price_valid_to = None
        self.total = ''

    def populate(self, row):
        super().populate(row)
        component_rows = row.tbody.findChildren('tr')
        for r in component_rows:
            name_sku_list = r.find('td', class_='component-name').text.strip().replace('\t', '').split('\n')
            name = name_sku_list[0]
            sku = name_sku_list[1]
            # qty = r.find('td', class_='quantity').text.strip()
            component_obj = Component(name, sku)
            self.description.configuration.append(component_obj)

    def __str__(self):
        components_string = ''
        for c in self.description.configuration:
            components_string += str(c) + '\n'
        return components_string



