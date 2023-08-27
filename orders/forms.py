from django.forms import inlineformset_factory
from decimal import Decimal,ROUND_HALF_UP
from utils.rates import get_current_euro_exchange_rate
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache


from django import forms
from .models import Order, OrderItem, OrderStatus, Stock, Company, Product, OrderItemTemplate, Employee, Technique
from account.models import UserCompany


class ReadOnlyTextInput(forms.widgets.TextInput):
    '''Клас для створення текстового поля, доступного лише для читання.'''

    def __init__(self, attrs=None, **kwargs):
        if attrs is None:
            attrs = {}
        attrs['readonly'] = True
        super().__init__(attrs, **kwargs)


class BaseOrderCreateForm(forms.ModelForm):
    '''
    Базовий клас для створення нових об'єктів Order зі спільними властивостями.
    '''
    status = forms.CharField(widget=ReadOnlyTextInput,label=_('status'))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Задає правила та обмеження для полів.

        # Перевірка помітки екземплярів на видалення.
        try:
            template_queryset = OrderItemTemplate.objects.filter(
                user_company__profile__user=self.request.user, is_deleted=False)
        except OrderItemTemplate.DoesNotExist:
            template_queryset = {}

        user_company_queryset = UserCompany.objects.filter(
            profile__user=self.request.user, is_deleted=False)

        try:
            company_queryset = Company.objects.filter(
                users_companies__in=user_company_queryset)
        except Company.DoesNotExist:
            company_queryset = {}

        try:
            stock_queryset = Stock.objects.filter(
                company__in=company_queryset, is_deleted=False)
        except Stock.DoesNotExist:
            stock_queryset = {}

        try:
            responsible_person_queryset = Employee.objects.filter(
                stocks_employee__in=stock_queryset, is_deleted=False).distinct()
        except Employee.DoesNotExist:
            stock_queryset = {}

        try:
            VIN_code_queryset = Technique.objects.filter(
                company__in=company_queryset, is_deleted=False)
        except Technique.DoesNotExist:
            VIN_code_queryset = {}

        self.fields['template'].queryset = template_queryset
        self.fields['company'].queryset = company_queryset
        self.fields['stock'].queryset = stock_queryset
        self.fields[
            'signatory_of_documents'].queryset = responsible_person_queryset
        self.fields['VIN_code'].queryset = VIN_code_queryset
        self.fields['status'].initial = OrderStatus.DRAFT.value
        self.fields['formed'].initial = self.request.user.get_full_name()

    class Meta:
        model = Order
        fields = ('status', 'template', 'company', 'formed', 'stock',
                  'signatory_of_documents', 'address',
                  'services_description', 'comments',
                  'VIN_code')

class DraftOrderCreateForm(BaseOrderCreateForm):
    '''
    Створює нові об'єкти Order із статусом DRAFT.
    '''

class OrderCreateForm(BaseOrderCreateForm):
    '''
    Створює нові об'єкти Order із статусом ORDER.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = OrderStatus.ORDER.value


class OrderForm(forms.ModelForm):
    '''Встановлює значення додаткової інформації у замовленні.'''
    status = forms.CharField(widget=ReadOnlyTextInput,label=_('status'))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)



        if self.instance.status == OrderStatus.ORDER.value or self.instance.status == OrderStatus.DRAFT.value and self.instance.user != self.request.user:
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.widget.attrs['disabled'] = True


        elif self.instance.status == OrderStatus.DRAFT.value:
            fields_to_disable = ['edrpou_code', 'first_and_last_name', 'email']
            for name, field in self.fields.items():
                if name in fields_to_disable:
                    field.widget.attrs['readonly'] = True



        # Задаємо правила та обмеження для полів.
        # Редагування існуючих замовлень залишаємо без обмеження 'is_deleted'.


        template_queryset = OrderItemTemplate.objects.filter(
            user_company__profile__user=self.request.user)

        user_company_queryset = UserCompany.objects.filter(
            profile__user=self.request.user)

        company_queryset = Company.objects.filter(
            users_companies__in=user_company_queryset)

        stock_queryset = Stock.objects.filter(
            company__in=company_queryset)

        responsible_person_queryset = Employee.objects.filter(
            stocks_employee__in=stock_queryset).distinct()

        VIN_code_queryset = Technique.objects.filter(
            company__in=company_queryset)

        self.fields['template'].queryset = template_queryset
        self.fields['company'].queryset = company_queryset
        self.fields['stock'].queryset = stock_queryset
        self.fields[
            'signatory_of_documents'].queryset = responsible_person_queryset
        self.fields['VIN_code'].queryset = VIN_code_queryset

    class Meta:
        model = Order
        fields = (
            'status', 'template', 'first_and_last_name', 'email', 'formed',
            'company', 'edrpou_code', 'stock',
            'signatory_of_documents', 'VIN_code', 'address',
            'services_description', 'comments',)


class OrderItemForm(forms.ModelForm):
    ''' Визначає значення таб. частини товарів в замовленні.'''

    product_name = forms.CharField(widget=ReadOnlyTextInput)
    product_description = forms.CharField(widget=ReadOnlyTextInput)

    pre_cost = forms.DecimalField()
    ord_cost = forms.DecimalField()
    pre_cost_with_vat = forms.DecimalField()
    ord_cost_with_vat = forms.DecimalField()

    pre_cost_ua = forms.DecimalField()
    ord_cost_ua = forms.DecimalField()
    pre_cost_with_vat_ua = forms.DecimalField()
    ord_cost_with_vat_ua = forms.DecimalField()



    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


        if self.instance.order.status == OrderStatus.ORDER.value or self.instance.order.status == OrderStatus.DRAFT.value and self.instance.order.user != self.request.user:
            rate = self.instance.order.rate
            readonly_fields = ['product', 'product_name', 'pre_quantity', 'ord_quantity', 'price', 'pre_cost', 'ord_cost','pre_cost_with_vat','ord_cost_with_vat', 'pre_cost_ua', 'ord_cost_ua', 'pre_cost_with_vat_ua', 'ord_cost_with_vat_ua']


        elif self.instance.order.status == OrderStatus.DRAFT.value:
            # Кешування курсу євро НБУ
            rate = cache.get('current_euro_exchange_rate')
            if not rate:
                rate = get_current_euro_exchange_rate()
                cache.set('current_euro_exchange_rate', rate, 60 * 60)

            readonly_fields = ['product', 'product_name', 'pre_quantity', 'price', 'pre_cost', 'ord_cost','pre_cost_with_vat','ord_cost_with_vat','pre_cost_ua', 'ord_cost_ua', 'pre_cost_with_vat_ua', 'ord_cost_with_vat_ua']

        else:
            readonly_fields = []

        for field_name in readonly_fields:
            self.fields[field_name].widget.attrs['readonly'] = True

        # Обмежуємо queryset для поля product тільки тими товарами,
        # які зв'язані з поточним замовленням (order)
        self.fields['product'].queryset = Product.objects.filter(order_items__order=self.instance.order)

        if self.instance.product:
            self.fields['product_name'].initial = self.instance.product.name
            self.fields['product_name'].label = 'Product'
            self.fields['product_description'].initial =  self.instance.product.description
            self.fields['product_name'].label = 'Product'
            self.fields['pre_cost'].initial = self.instance.pre_get_cost()
            self.fields['ord_cost'].initial = self.instance.ord_get_cost()
            self.fields['pre_cost_with_vat'].initial = self.instance.pre_get_cost_with_vat()
            self.fields['ord_cost_with_vat'].initial = self.instance.ord_get_cost_with_vat()

            pre_cost_ua_value = self.instance.pre_get_cost() * rate
            self.fields['pre_cost_ua'].initial = Decimal(pre_cost_ua_value).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            ord_cost_ua_value = self.instance.ord_get_cost() * rate
            self.fields['ord_cost_ua'].initial = Decimal(ord_cost_ua_value).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            pre_cost_with_vat_ua_value = self.instance.pre_get_cost_with_vat() * rate
            self.fields['pre_cost_with_vat_ua'].initial = Decimal(pre_cost_with_vat_ua_value).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            ord_cost_with_vat_ua_value = self.instance.ord_get_cost_with_vat() * rate
            self.fields['ord_cost_with_vat_ua'].initial = Decimal(ord_cost_with_vat_ua_value).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'pre_quantity', 'ord_quantity', 'price', 'pre_cost', 'ord_cost', 'pre_cost_with_vat', 'ord_cost_with_vat', 'pre_cost_ua', 'ord_cost_ua', 'pre_cost_with_vat_ua', 'ord_cost_with_vat_ua']



'''Зв"язує моделі Order та OrderItem'''
OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm,
                                         extra=0, can_delete=False, )
