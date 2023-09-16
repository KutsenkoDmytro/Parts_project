from decimal import Decimal, ROUND_HALF_UP
from utils.rates import get_current_euro_exchange_rate
from django.conf import settings
from django.core.cache import cache

from shop.models import Product
from orders.functions import get_time_until_end_of_day


class Cart(object):

    def __init__(self, request, user=None):
        '''Ініціалізація об'єкта кошика.'''
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Зберігаємо порожній кошик у сесії.
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.user = user

    def add(self, product, quantity=1, update_quantity=False):
        '''Додавання товару до кошика або оновлення його кількості.'''
        product_id = str(product.id)
        user = self.user

        if product_id not in self.cart:
            # Отримуємо користувацький прайс із методу.
            self.cart[product_id] = {'quantity': 0, 'price': str(product.get_price_with_coefficient(user))}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()


    def save(self):
        '''Позначаємо сесію як змінену.'''
        self.session.modified = True

    def remove(self, product):
        '''Видалення товару з кошика.'''
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.save()

    def __iter__(self):
        '''Переходимо по товарам кошика та отримуємо відповідні об'єкти Product.'''
        # Перетворюємо dict_keys на список.
        product_ids = list(self.cart.keys())
        # Отримуємо об'єкти моделі Product та передаємо їх в корзину.
        products = Product.objects.filter(id__in=product_ids)

        # Виконуємо попереднє завантаження (select_related) категорії для кожного товару,
        products = products.select_related('category')
        cart = self.cart.copy()

        # Кешування курсу євро НБУ.
        rate = cache.get('current_euro_exchange_rate')
        if not rate:
            rate = get_current_euro_exchange_rate()
            cache.set('current_euro_exchange_rate',rate,get_time_until_end_of_day())

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            price = Decimal(item['price'])
            quantity = item['quantity']
            total_price = price * quantity
            cost_with_vat = total_price * settings.VAT_RATE
            cost_ua = total_price * rate
            cost_with_vat_ua = cost_with_vat * rate

            item.update({
                'price': price,
                'total_price': total_price,
                'cost_with_vat': cost_with_vat.quantize(Decimal('0.00'),
                                                        rounding=ROUND_HALF_UP),
                'cost_ua': cost_ua.quantize(Decimal('0.00'),
                                            rounding=ROUND_HALF_UP),
                'cost_with_vat_ua': cost_with_vat_ua.quantize(Decimal('0.00'),
                                                              rounding=ROUND_HALF_UP)
            })

        for item in cart.values():
            yield item.copy()

    def __len__(self):
        '''Повертає загальну кількість товарів в кошику.'''
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        '''Повертає загальну суму товарів в кошику у євро без ПДВ.'''
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_total_cost_with_vat(self):
        '''Повертає загальну суму товарів в кошику у грн. з ПДВ.'''
        total_cost_with_vat = sum(
            Decimal(item['price']) * item['quantity'] * settings.VAT_RATE
            for item in self.cart.values()
        )
        return round(total_cost_with_vat,2)

    def get_total_cost_ua(self):
        '''Повертає загальну суму товарів в кошику у грн. без ПДВ.'''
        # Кешування курсу євро НБУ.
        rate = cache.get('current_euro_exchange_rate')
        if not rate:
            rate = get_current_euro_exchange_rate()
            cache.set('current_euro_exchange_rate', rate, get_time_until_end_of_day())

        total_cost_ua = sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        ) * rate

        return total_cost_ua.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    def get_total_cost_with_vat_ua(self):
        '''Повертає загальну суму товарів в кошику в євро з ПДВ.'''
        # Кешування курсу євро НБУ.
        rate = cache.get('current_euro_exchange_rate')
        if not rate:
            rate = get_current_euro_exchange_rate()
            cache.set('current_euro_exchange_rate', rate, get_time_until_end_of_day())

        total_cost_with_vat = sum(
            Decimal(item['price']) * item['quantity'] * settings.VAT_RATE
            for item in self.cart.values()
        ) * rate
        return total_cost_with_vat.quantize(Decimal('0.00'),
                                            rounding=ROUND_HALF_UP)


    def clear(self):
        '''Очищення кошику.'''
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def count_unique_items(self):
        '''Підраховує загальну кількість унікальних товарів в кошику.'''
        return len(self.cart)
