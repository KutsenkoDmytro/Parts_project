import os
import sys
import xlrd

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '..')))

import django

django.setup()
from shop.models import Product


class UploadingProducts(object):
    '''Для обновления или добавления товаров в таблицу "Товары".'''
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

        product_bulk_list = list()
        for row in range(1, s.nrows):
            row_dict = {}
            for column in range(s.ncols):
                value = s.cell(row, column).value
                field_name = headers[column]

                if field_name == 'id' and not value:
                    continue

                if field_name in self.foreign_key_fields:
                    related_model = self.getting_related_model(field_name)

                    instance, created = related_model.objects.get_or_create(
                        name=value)
                    value = instance

                row_dict[field_name] = value


            product_bulk_list.append(self.model(**row_dict))

        Product.objects.bulk_create(product_bulk_list)

        return True


class UploadingCart(object):
    '''Для последубщей загрузки товаров в "Корзину".'''
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
        result_dict = {'data': []}  # Добавляем новый ключ в словарь result_dict
        error_messages = []  # Создаем список для ошибок значений product
        uploaded_file = self.uploaded_file
        # Проверяем, открыт ли файл нужного формата .xls.
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

        # Добавляем сообщение об ошибке в словарь result_dict, если таковое имеется
        if error_messages:
            result_dict['error'] = ", ".join(error_messages)
        return result_dict
