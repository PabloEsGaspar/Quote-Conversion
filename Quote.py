
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

    def __init__(self, quote_number, purchaser_name, purchaser_email, purchaser_phone, created_by, date_created,
                 expiration_date, subtotal, quote_total, contract_name, list_of_products, special_pricing_code):
        self.quote_number = quote_number
        self.purchaser_name = purchaser_name
        self.purchaser_email = purchaser_email
        self.purchaser_phone = purchaser_phone
        self.created_by = created_by
        self.date_created = date_created
        self.expiration_date = expiration_date
        self.subtotal = subtotal
        self.quote_total = quote_total
        self.contract_name = contract_name
        self.special_pricing_code = special_pricing_code
        self.list_of_products = list_of_products

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





