import os
import sys
import xlrd

os.environ['DJANGO_SETTINGS_MODULE'] = 'parts_project.settings'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '..')))

import django

django.setup()
from shop.models import Product


class UploadingProducts(object):
    '''Оновлення або додавання продуктів до моделі "Товари".'''
    foreign_key_fields = ['category']
    model = Product

    def __init__(self, data):
        self.data = data
        self.uploaded_file = data.get('file')
        self.parsing()

    def getting_related_model(self, field_name):
        related_model = self.model._meta.get_field(
            field_name).remote_field.model
        return related_model

    def getting_headers(self):
        s = self.s
        headers = dict()
        for column in range(s.ncols):
            value = s.cell(0, column).value
            headers[column] = value
        return headers

    def parsing(self):
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s

        headers = self.getting_headers()
        existing_product_ids = set(Product.objects.values_list('id', flat=True))

        #product_bulk_list = list()
        for row in range(1, s.nrows):
            row_dict = {}
            for column in range(s.ncols):
                value = s.cell(row, column).value
                field_name = headers[column]

                if field_name == 'id' and not value:
                    continue

                #if field_name == 'price' and ',' in value:
                #    value = value.replace(',', '.')

                if field_name in self.foreign_key_fields:
                    related_model = self.getting_related_model(field_name)

                    instance, created = related_model.objects.get_or_create(
                        name=value)
                    value = instance

                row_dict[field_name] = value

            # Отримання значення id для пошуку або оновлення
            product_id = row_dict.pop('id', None)

            if product_id in existing_product_ids:
                # Оновити існуючий запис
                Product.objects.filter(id=product_id).update(**row_dict)
            else:

                # Створити новий запис
                new_product = Product.objects.create(**row_dict)
                # Додаємо id в список
                #existing_product_ids.add(new_product.id)


            #product_bulk_list.append(self.model(**row_dict))
            #Product.objects.create(**row_dict)
        #Product.objects.bulk_create(product_bulk_list)

        return True


class UploadingCart(object):
    '''Для завантаження товару в «Кошик».'''
    model = Product

    def __init__(self, data):
        self.data = data
        self.uploaded_file = data.get('file')
        self.result_dict = self.parsing()

    def getting_headers(self):
        s = self.s
        headers = dict()
        for column in range(s.ncols):
            value = s.cell(0, column).value
            headers[column] = value
        return headers

    def parsing(self):
        result_dict = {'data': []}  # Додаємо новий ключ в словник result_dict
        error_messages = []  # Створюємо список для помилок значень product
        uploaded_file = self.uploaded_file
        # Перевіряємо, чи відкрито файл потрібного формату .xls.
        try:
            wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        except xlrd.XLRDError as e:
            error_file = f"'{str(e)}'"
            result_dict['error_file'] = error_file
            return result_dict

        s = wb.sheet_by_index(0)
        self.s = s

        headers = self.getting_headers()

        for row in range(1, s.nrows):
            row_dict = {}
            for column in range(s.ncols):
                value = s.cell(row, column).value
                field_name = headers[column]

                if field_name == 'id' and not value:
                    continue

                if field_name == 'product':
                    try:
                        value = str(int(value))
                    except ValueError:
                        value = str(value)

                    product_name = value
                    product = Product.objects.filter(name=product_name).first()
                    if product:
                        value = product
                    else:
                        error_messages.append(f"'{product_name}'")
                        break

                row_dict[field_name] = value

            if row_dict:
                result_dict['data'].append(row_dict)

        # Додаємо повідомлення про помилку в словник result_dict, якщо воно є.
        if error_messages:
            result_dict['error'] = ", ".join(error_messages)
        return result_dict