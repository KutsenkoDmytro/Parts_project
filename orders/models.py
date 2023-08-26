from django.db import models
from enum import Enum
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from django.utils.translation import gettext_lazy as _

from shop.models import Product
from account.models import OrderItemTemplate
from customer.models import Company, Stock, Employee, Technique

class OrderStatus(Enum):
    '''Визначає перелік статусів замовлень.'''
    DRAFT = 'draft'
    ORDER = 'order'


class Order(models.Model):
    '''Визначає супутню інформацію для замовлення.'''
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,verbose_name=_('user'))

    status = models.CharField(max_length=10,
                              choices=[(tag.value, tag.name) for tag in
                                       OrderStatus],
                              default=OrderStatus.DRAFT.value, verbose_name=_('status'))

    template = models.ForeignKey(OrderItemTemplate,
                                 related_name='orders_templates',
                                 on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('template'))

    first_and_last_name = models.CharField(max_length=100, verbose_name=_('first and last name'))
    email = models.EmailField(verbose_name=_('e-mail'))
    formed = models.CharField(max_length=100, verbose_name=_('formed'))
    company = models.ForeignKey(Company,
                                related_name='orders_companies',
                                on_delete=models.CASCADE, verbose_name=_('company'))

    edrpou_code = models.IntegerField(verbose_name=_('edrpou code'))

    stock = models.ForeignKey(Stock, related_name='orders_stocks',
                              on_delete=models.CASCADE, verbose_name=_('stock'))

    signatory_of_documents = models.ForeignKey(Employee,
                                               related_name='orders_employees',
                                               on_delete=models.CASCADE, verbose_name=_('signatory of documents'))

    address = models.TextField(max_length=200, verbose_name=_('address'))

    services_description = models.TextField(max_length=200, blank=True, verbose_name=_('services description'))

    comments = models.TextField(max_length=200, blank=True, verbose_name=_('comments'))

    VIN_code = models.ForeignKey(Technique,
                                 related_name='orders_technique',
                                 on_delete=models.CASCADE, null=True,
                                 blank=True, verbose_name=_('VIN code'))
    rate = models.DecimalField(max_digits=8, decimal_places=4, blank=True,default=1.0, verbose_name=_('rate'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.ord_get_cost() for item in self.items.all())

    def get_total_cost_with_vat(self):
        total_cost_with_vat = sum(item.ord_get_cost() for item in self.items.all())* Decimal('1.2')
        return total_cost_with_vat.quantize(Decimal('0.00'),
                                            rounding=ROUND_HALF_UP)
    def get_total_cost_with_vat_ua(self):
        total_cost_with_vat_ua = sum(item.ord_get_cost() for item in self.items.all())* Decimal('1.2')*self.rate
        return total_cost_with_vat_ua.quantize(Decimal('0.00'),
                                            rounding=ROUND_HALF_UP)



    def save(self, *args, **kwargs):
        '''
        Збереження моделі з валідацією та заповненням значень edrpou_code та
        first_and_last_name якщо вони не вказані, а потім зберігає
        екземпляр в базі даних.
        '''
        if not self.edrpou_code:
            self.edrpou_code = self.company.edrpou_code
        if not self.first_and_last_name:
            self.first_and_last_name = self.user.get_full_name()

        super().save(*args, **kwargs)


class OrderItem(models.Model):
    '''Інформація про кількість товарів у замовленні.'''
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE, verbose_name=_('order'))
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE, verbose_name=_('product'))

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price'))
    pre_quantity = models.PositiveIntegerField(default=1, verbose_name=_('pre quantity'))
    ord_quantity = models.PositiveIntegerField(default=0, verbose_name=_('order quantity'))

    def __str__(self):
        return '{}'.format(self.id)

    def pre_get_cost(self):
        return self.price * self.pre_quantity

    def ord_get_cost(self):
        return self.price * self.ord_quantity

    def pre_get_cost_with_vat(self):
        item_cost_with_vat = self.price * self.pre_quantity * Decimal('1.2')
        return item_cost_with_vat.quantize(Decimal('0.00'),
                                            rounding=ROUND_HALF_UP)
    def ord_get_cost_with_vat(self):
        item_cost_with_vat = self.price * self.ord_quantity * Decimal('1.2')
        return item_cost_with_vat.quantize(Decimal('0.00'),
                                            rounding=ROUND_HALF_UP)

    '''
     @property для визначення методу product_name як властивості. 
     Коли ми отримуємо доступ до цієї властивості, вона повертає ім'я продукту, 
     пов'язаний з об'єктом OrderItem за допомогою атрибута name об'єкта Product.
    '''

    @property
    def product_name(self):
        return self.product.name

    '''
    Сеттер атрибута product_name, який встановлює значення
    для атрибуту name об'єкту Product та зберігає його в базі даних.
    '''

    @product_name.setter
    def product_name(self, value):
        self.product.name = value
        self.product.save()





