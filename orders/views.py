from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, \
    Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from utils.rates import get_euro_exchange_rate, get_current_euro_exchange_rate
import xlwt
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.formats import number_format
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q

from .models import OrderItem, Order, Stock, Employee, \
    OrderItemTemplate, Company, Technique
from .forms import DraftOrderCreateForm, OrderCreateForm, OrderForm, \
    OrderItemFormSet, OrderStatus
from cart.cart import Cart
from account.models import Profile, UserCompany
from utils.emails import SendingEmail
from .functions import format_date, datetime


@login_required
def order_create(request):
    '''Обробник для створення затвердженого замовлення.'''
    cart = Cart(request)

    # Крок 1: Збираємо всі категорії продуктів з корзини.
    categories_in_cart = set(item['product'].category for item in cart)

    if len(categories_in_cart) > 1:
        # Крок 2: Перевіряємо, чи всі продукти мають однакову категорію.
        ms_part_1 = _(
            'Error: All items in your cart must belong to the same category! Categories in your order:')
        categories_list = ', '.join(
            [category.name for category in categories_in_cart])
        messages.error(request, f'{ms_part_1} {categories_list}.')
        return HttpResponseRedirect(reverse('cart:cart_detail'))

    if request.method == 'POST':
        form = OrderCreateForm(data=request.POST, request=request)
        if form.is_valid():

            order = form.save(commit=False)
            order.user = request.user
            order.email = request.user.email

            rate = cache.get('current_euro_exchange_rate')
            if not rate:
                rate = get_current_euro_exchange_rate()
                cache.set('current_euro_exchange_rate', rate, 60 * 60)

            order.rate = rate
            order = form.save()

            for item in cart:
                # Для затвердженого замовлення 'ord_quantity' заповняємо відповідним значенням 'pre_quantity'.
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         pre_quantity=item['quantity'],
                                         ord_quantity=item['quantity'])
            # Очищуємо кошик.
            cart.clear()

            # Відправляємо листи адміну та користувачу.
            email = SendingEmail()
            email.sending_email(type_id=1, email=order.email, order=order)
            # Використовувати для відпраки листа тільки користувачу.
            # email.sending_email(type_id=2, email=order.email, order=order)

            # Отримання номера замовлення.
            order_number = order.id
            # Додання номеру замовлення до повідомлення про успішне створення замовлення.
            ms_part_1 = _(
                'The order has been successfully formed. Your order number:')
            ms_part_2 = _('Thanks!')
            success_message = f'{ms_part_1} {order_number}. {ms_part_2}'
            messages.success(request, success_message)

            return HttpResponseRedirect(reverse('orders:orders'))

        else:
            messages.error(request,
                           _('Error when placing or editing an order, check the form data!'))
    else:
        form = OrderCreateForm(request=request)

    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})


@login_required
def draft_order_create(request):
    '''Обробник для створення чернетки замовлення.'''
    cart = Cart(request)

    # Крок 1: Збираємо всі категорії продуктів з корзини.
    categories_in_cart = set(item['product'].category for item in cart)

    if len(categories_in_cart) > 1:
        # Крок 2: Перевіряємо, чи всі продукти мають однакову категорію.
        ms_part_1 = _(
            'Error: All items in your cart must belong to the same category! Categories in your order:')
        categories_list = ', '.join(
            [category.name for category in categories_in_cart])
        messages.error(request, f'{ms_part_1} {categories_list}.')
        return HttpResponseRedirect(reverse('cart:cart_detail'))


    if request.method == 'POST':
        form = DraftOrderCreateForm(data=request.POST, request=request)
        if form.is_valid():

            order = form.save(commit=False)
            order.user = request.user
            order.email = request.user.email

            rate = cache.get('current_euro_exchange_rate')
            if not rate:
                rate = get_current_euro_exchange_rate()
                cache.set('current_euro_exchange_rate', rate, 60 * 60)

            order.rate = get_current_euro_exchange_rate()

            order = form.save()

            for item in cart:
                # Для чернетки замовлення 'ord_quantity' заповнюємо відповідним значенням 0.
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         pre_quantity=item['quantity'],
                                         ord_quantity=0)
            # Очищуємо кошик.
            cart.clear()
            # Отримання номера чернетки замовлення.
            order_number = order.id
            # Додавання номера чернетки замовлення до повідомлення про успішне створення.
            ms_part_1 = _(
                'The draft order has been successfully formed. Number:')
            success_message = f'{ms_part_1} {order_number}.'
            messages.success(request, success_message)

            return HttpResponseRedirect(reverse('orders:orders'))

        else:
            messages.error(request,
                           _('There was an error while placing or editing the draft order, check the form data!'))
    else:
        form = DraftOrderCreateForm(request=request)
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})


@login_required
def get_all_order_header_options(request):
    '''
    Призначений для обробки AJAX-запиту та повернення JSON-відповіді із списком
    варіантів для полів company, stock, signatory_of_documents, коли користувач
    не вказав конкретний шаблон.
    '''

    user_company_queryset = UserCompany.objects.filter(
        profile__user=request.user, is_deleted=False)

    try:
        company_queryset = Company.objects.filter(
            users_companies__in=user_company_queryset)
        company_options = {str(company.id): company.name for company in
                           company_queryset}
    except Company.DoesNotExist:
        company_options = {}

    try:
        stock_queryset = Stock.objects.filter(
            company__in=company_queryset, is_deleted=False)
        stock_options = {str(stock.id): stock.name for stock in stock_queryset}
    except Company.DoesNotExist:
        stock_options = {}

    try:
        signatory_of_documents_options_queryset = Employee.objects.filter(
            stocks_employee__in=stock_queryset, is_deleted=False)
        signatory_of_documents_options = {
            str(signatory_of_documents.id): signatory_of_documents.get_full_name()
            for signatory_of_documents in
            signatory_of_documents_options_queryset}
    except Employee.DoesNotExist:
        signatory_of_documents_options = {}

    try:
        technique_queryset = Technique.objects.filter(
            company__in=company_queryset)
        technique_options = {str(technique.id): technique.serial_number for
                             technique in technique_queryset}
    except Employee.DoesNotExist:
        technique_options = {}

    data = {
        'company_options': company_options,
        'stock_options': stock_options,
        'signatory_of_documents_options': signatory_of_documents_options,
        'technique_options': technique_options,
    }

    return JsonResponse(data)


@login_required
def get_template_order_header_options(request):
    '''
    Призначений для обробки AJAX-запиту та повернення JSON-відповіді із списком
    варіантів для полів company, stock, signatory_of_documents залежно від
    обраного значення у полі template.
    '''
    template_id = request.GET.get('template_id')

    user_company_id = UserCompany.objects.get(
        orders_item_templates_user_company__id=template_id).id
    try:
        company = Company.objects.get(users_companies__id=user_company_id,
                                      is_deleted=False)
        company_options = {str(company.id): company.name}
    except Company.DoesNotExist:
        company_options = {}

    try:
        stock = Stock.objects.get(
            orders_item_templates_stock__id=template_id, is_deleted=False)
        stock_options = {str(stock.id): stock.name}
    except Stock.DoesNotExist:
        stock_options = {}

    try:
        signatory_of_documents = Employee.objects.get(
            orders_item_templates_employee__id=template_id, is_deleted=False)
        signatory_of_documents_options = {
            str(signatory_of_documents.id): signatory_of_documents.get_full_name()}
    except Employee.DoesNotExist:
        signatory_of_documents_options = {}

    try:
        technique_queryset = Technique.objects.filter(
            company=company, is_deleted=False)
        technique_options = {str(technique.id): technique.serial_number for
                             technique in technique_queryset}
    except Technique.DoesNotExist:
        technique_options = {}

    address = OrderItemTemplate.objects.get(id=template_id).address

    data = {
        'company_options': company_options,
        'stock_options': stock_options,
        'signatory_of_documents_options': signatory_of_documents_options,
        'address': address,
        'technique_options': technique_options,
    }

    return JsonResponse(data)


@login_required
def get_stock_options(request):
    '''
    Призначений для обробки AJAX-запиту та повернення JSON-відповіді із списком
    варіантів для поля stock в залежності від обраного значення у полі company
    та також значення edrpou_code.
    '''
    company_id = request.GET.get('company_id')

    company = Company.objects.get(id=company_id)
    edrpou_code = company.edrpou_code

    try:
        stock_queryset = Stock.objects.filter(company=company, is_deleted=False)
        stock_options = {str(stock.id): stock.name for stock in stock_queryset}
    except Stock.DoesNotExist:
        stock_options = {}

    try:
        technique_queryset = Technique.objects.filter(company=company,
                                                      is_deleted=False)
        technique_options = {str(technique.id): technique.serial_number for
                             technique in technique_queryset}
    except Technique.DoesNotExist:
        technique_options = {}

    data = {
        'technique_options': technique_options,
        'stock_options': stock_options,
        'edrpou_code': edrpou_code
    }

    return JsonResponse(data)


@login_required
def get_signatory_of_documents_options(request):
    '''
    Призначений для обробки AJAX-запиту та повернення JSON-відповіді із списком
    варіантів для поля signatory_of_documents в залежності від обраних значень
    у полях stock та user_company.
    '''

    stock_id = request.GET.get('stock')

    try:
        signatory_of_documents = Employee.objects.get(
            stocks_employee__id=stock_id)
        signatory_of_documents_options = {
            str(signatory_of_documents.id): signatory_of_documents.get_full_name()}
    except Technique.DoesNotExist:
        signatory_of_documents_options = {}

    return JsonResponse(
        {'signatory_of_documents_options': signatory_of_documents_options})


def merging_dicts(l1, l2, key1, key2):
    merged = {}
    for item in l1:
        merged[item[key1]] = item

    for item in l2:
        try:
            if 'products' in merged[item[key2]]:
                merged[item[key2]]['products'].append(item)
            else:
                merged[item[key2]]['products'] = [item]

        except Exception as e:
            return None

    orders = [val for (_, val) in merged.items()]
    return orders


@login_required
def orders(request):
    '''Повертає список замовлень.'''
    query_search = request.GET.get('search')

    user = request.user
    profile = get_object_or_404(Profile,user=user)
    role = profile.role.name

    orders = Order.objects.select_related('user', 'template', 'company',
                                          'stock',
                                          'signatory_of_documents').values(
        'status', 'id', 'created', 'company__name', 'first_and_last_name',
        'formed')
    if query_search:
        orders = orders.filter(
            Q(status__icontains=query_search) |
            Q(id__icontains=query_search) |
            Q(created__icontains=query_search) |
            Q(company__name__icontains=query_search) |
            Q(first_and_last_name__icontains=query_search) |
            Q(formed__icontains=query_search)
        )

    if role == 'user':
        orders = orders.filter(
            user=user)
    elif role == 'company_admin':
        # Отримати ідентифікатори компаній, пов'язаних з поточним profile через UserCompany.
        user_companies = UserCompany.objects.filter(profile=profile)
        company_ids = user_companies.values_list('company', flat=True)

        # Фільтрувати замовлення за списком ідентифікаторів компаній.
        orders = orders.filter(company__in=company_ids)
    elif role == 'holding_admin':
        orders = orders.filter(company__holding=profile.holding)
    elif role == 'site_admin':
        orders = orders
    else:
        raise Http404('This role is not configured to display orders.')

    order_ids = [order['id'] for order in orders]

    products_in_order = OrderItem.objects.filter(
        order_id__in=order_ids).values(
        'order', 'product', 'product__name', 'product__description',
        'product__category__name', 'price',
        'pre_quantity',
        'ord_quantity',
    )

    orders = merging_dicts(list(orders), list(products_in_order), 'id',
                           'order')

    for order in orders:
        total = Decimal('0.00')
        total_with_VAT = Decimal('0.00')
        total_products = 0

        for item in order['products']:
            total_item = item['ord_quantity'] * item['price']
            total += total_item
            total_with_VAT += total_item * settings.VAT_RATE
            if item['ord_quantity'] > 0:
                total_products += 1

        order['total'] = round(total, 2)
        order['total_with_VAT'] = round(total_with_VAT, 2)
        order['total_products'] = total_products

    paginator = Paginator(orders, 10)  # Показувати 10 замовлень на сторінці
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orders/orders.html', {'page_obj': page_obj})


@login_required
def edit_order(request, order_id):
    '''Обробник для редагування замовлення.'''
    user = request.user
    order = get_object_or_404(Order, pk=order_id)
    if user.is_superuser or order.company.holding == user.profile.holding:

        created = order.created
        updated = order.updated

        # Якщо замовлення підтверджено, курс залишається на дату останнього оновлення.
        # (підтвердження замовлення), в іншому випадку: курс встановлюється на поточну дату.

        if order.status == 'order':
            confirmation_date = updated
            rate = order.rate

        elif order.status == 'draft':

            confirmation_date = datetime.now()
            formatted_date = format_date(confirmation_date)

            # Кушування курсу євро НБУ
            cache_key = f"{formatted_date}_euro_exchange_rate"

            rate = cache.get(cache_key)
            if not rate:
                rate = get_euro_exchange_rate(formatted_date)
                cache.set(cache_key, rate, 60 * 60)

        total = order.get_total_cost()
        total_with_vat = order.get_total_cost_with_vat()

        total_ua = round(total * rate, 2)
        total_with_vat_ua = round(total_with_vat * rate, 2)

        if request.method == 'POST':
            order_form = OrderForm(request.POST, instance=order, request=request)
            order_item_formset = OrderItemFormSet(request.POST, instance=order,
                                                  form_kwargs={'request': request})

            if order_form.is_valid() and order_item_formset.is_valid():
                order_form.save()
                for item in order_item_formset:
                    item.save()

                # Перевірка, чи не перевищує яка-небудь ord_quantity значення 0.
                has_ord_quantity = any(
                    [form.cleaned_data['ord_quantity'] > 0 for form in
                     order_item_formset]
                )

                # Оновлюємо статус якщо істина.
                if has_ord_quantity:
                    order.status = OrderStatus.ORDER.value

                    # Якщо користувач підтверджує замовлення, курс записується на поточну дату.
                    order.rate = rate

                    order.save()

                    # Відправляємо листи адміну та користувачу.
                    email = SendingEmail()
                    email.sending_email(type_id=1, email=order.email, order=order)
                    # Використовувати для відпраки листа тільки користувачу.
                    # email.sending_email(type_id=2, email=order.email, order=order).

                    # Отримання номер замовлення.
                    order_number = order.id
                    # Додавання номера замовлення до повідомлення про успішне створення замовлення.
                    ms_part_1 = _(
                        'The order has been successfully formed. Your order number:')
                    ms_part_2 = _('Thanks!')
                    success_message = f'{ms_part_1} {order_number}. {ms_part_2}'
                    messages.success(request, success_message)

                # Перенаправлення на сторінку, якщо дія успішна.
                return HttpResponseRedirect(reverse('orders:orders'))
            else:
                messages.error(request,
                               _('Error when placing or editing an order, check the form data!'))

        else:
            order_form = OrderForm(instance=order, request=request)
            order_item_formset = OrderItemFormSet(instance=order,
                                                  form_kwargs={'request': request})

        return render(request, 'orders/order/edit_order.html', {
            'user_in_session': user,
            'order': order,
            'order_form': order_form,
            'order_item_formset': order_item_formset,
            'total': total,
            'total_with_vat': total_with_vat,
            'created': created,
            'updated': updated,
            'confirmation_date': confirmation_date,
            'euro_rate': rate,
            'total_ua': total_ua,
            'total_with_vat_ua': total_with_vat_ua,

        })
    else:
        return Http404


@login_required
def excel_detail(request, order_id):
    response = HttpResponse(content_type='application/ms-excel')
    options = str(f'attachment; filename=WebOrder_{order_id}_AstraLTD.xls')

    response['Content-Disposition'] = options

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [str(_('Attribute')), str(_('Value'))]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    order = Order.objects.select_related('user', 'template', 'company', 'stock',
                                         'signatory_of_documents',
                                         'VIN_code').get(
        pk=order_id)

    vat_rate = settings.VAT_RATE
    updated = order.updated

    if order.status == 'order':
        confirmation_date = updated
        rate = order.rate

    elif order.status == 'draft':

        confirmation_date = datetime.now()
        formatted_date = format_date(confirmation_date)

        # Кушування курсу євро НБУ
        cache_key = f"{formatted_date}_euro_exchange_rate"

        rate = cache.get(cache_key)
        if not rate:
            rate = get_euro_exchange_rate(formatted_date)
            cache.set(cache_key, rate, 60 * 60)

    fields = [
        (str(_('Status')), order.status),
        (str(_('WEB-order number')), order_id),
        (str(_('Created')), order.created.strftime(
            '%Y.%m.%d') if order.created else None),
        (str(_('Updated')), order.updated.strftime(
            '%Y.%m.%d') if order.updated else None),
        (str(_('Exchange rate date')), confirmation_date.strftime(
            '%Y.%m.%d') if confirmation_date else None),
        (str(_('Rate (€)')), rate if rate else None),
        (str(_('User')), order.user.username if order.user else None),
        (str(_('First and last name')),
         order.first_and_last_name if order.first_and_last_name else None),
        ('Email', order.email if order.email else None),
        (str(_('Company')), order.company.name if order.company else None),
        (str(_('edrpou code')), order.edrpou_code),
        (str(_('Formed')), order.formed if order.formed else None),
        (str(_('Stock')), order.stock.name if order.stock else None),
        (str(_('Signatory of documents')),
         order.signatory_of_documents.get_full_name() if order.signatory_of_documents else None),
        (str(_('VIN code')),
         order.VIN_code.serial_number if order.VIN_code else None),
        (str(_('Address')), order.address if order.address else None),
        (str(_('Services description')), order.services_description),
        (str(_('Comments')), order.comments),
    ]

    for field_num, field_value in enumerate(fields, start=1):
        ws.write(field_num, 0, field_value[0],
                 font_style)  # Записуємо назву поля в колонку "Поле".
        ws.write(field_num, 1, field_value[1],
                 font_style)  # Записуємо значення в колонку "Значення".

        # Записуємо інформацію про кожний OrderItem.
    row_num += len(
        fields) + 2  # Переміщуємось на наступний рядок після полів замовлення.

    order_items = order.items.all()  # Отримуємо всі OrderItem для даного замовлення.

    order_item_columns = ['№', str(_('Category')), str(_('Product')),
                          str(_('Description')), str(_('Price (€)')),
                          str(_('Pre quantity')),
                          str(_('Pre cost (€) without VAT')),
                          str(_('Pre cost (€) with VAT')),
                          str(_('Pre cost (₴) without VAT')),
                          str(_('Pre cost (₴) with VAT')),
                          str(_('Ord quantity')),
                          str(_('Ord cost (€) without VAT')),
                          str(_('Ord cost (€) with VAT')),
                          str(_('Ord cost (₴) without VAT')),
                          str(_('Ord cost (₴) with VAT'))]

    for col_num, col_value in enumerate(order_item_columns):
        ws.write(row_num, col_num, col_value, font_style)

    # Записуємо інформацію про кожний OrderItem.
    total_pre_amount = 0
    total_pre_amount_with_vat = 0
    total_pre_amount_ua = 0
    total_pre_amount_with_vat_ua = 0

    total_ord_amount = 0
    total_ord_amount_with_vat = 0
    total_ord_amount_ua = 0
    total_ord_amount_with_vat_ua = 0

    for index, order_item in enumerate(order_items, start=1):
        row_num += 1
        ws.write(row_num, 0, index,
                 font_style)  # Записуємо номер рядка (індекс) OrderItem.
        ws.write(row_num, 1, order_item.product.category.name,
                 font_style)
        ws.write(row_num, 2, order_item.product.name, font_style)
        ws.write(row_num, 3, order_item.product.description, font_style)
        ws.write(row_num, 4,
                 number_format(order_item.price, decimal_pos=2),
                 font_style)
        ws.write(row_num, 5, number_format(order_item.pre_quantity),
                 font_style)
        ws.write(row_num, 6,
                 number_format(
                     order_item.price * order_item.pre_quantity,
                     decimal_pos=2), font_style)
        ws.write(row_num, 7, number_format(
            order_item.price * order_item.pre_quantity * vat_rate,
            decimal_pos=2),
                 font_style)
        ws.write(row_num, 8, number_format(
            order_item.price * order_item.pre_quantity * rate,
            decimal_pos=2),
                 font_style)
        ws.write(row_num, 9, number_format(
            order_item.price * order_item.pre_quantity * vat_rate * rate,
            decimal_pos=2),
                 font_style)
        ws.write(row_num, 10, number_format(order_item.ord_quantity),
                 font_style)
        ws.write(row_num, 11, number_format(
            order_item.price * order_item.ord_quantity, decimal_pos=2),
                 font_style)
        ws.write(row_num, 12, number_format(
            order_item.price * order_item.ord_quantity * vat_rate,
            decimal_pos=2),
                 font_style)
        ws.write(row_num, 13, number_format(
            order_item.price * order_item.ord_quantity * rate,
            decimal_pos=2),
                 font_style)
        ws.write(row_num, 14, number_format(
            order_item.price * order_item.ord_quantity * vat_rate * rate,
            decimal_pos=2),
                 font_style)

        total_pre_amount += order_item.price * order_item.pre_quantity
        total_pre_amount_with_vat += round(
            order_item.price * order_item.pre_quantity * vat_rate, 2)
        total_pre_amount_ua += round(
            order_item.price * order_item.pre_quantity * rate, 2)
        total_pre_amount_with_vat_ua += round(
            order_item.price * order_item.pre_quantity * vat_rate * rate,
            2)

        total_ord_amount += order_item.price * order_item.ord_quantity
        total_ord_amount_with_vat += round(
            order_item.price * order_item.ord_quantity * vat_rate, 2)
        total_ord_amount_ua += round(
            order_item.price * order_item.ord_quantity * rate, 2)
        total_ord_amount_with_vat_ua += round(
            order_item.price * order_item.ord_quantity * vat_rate * rate,
            2)

        # Записуємо загальні суми.
    ws.write(row_num + 2, 5, str(_('Total')), font_style)
    ws.write(row_num + 2, 6, number_format(total_pre_amount), font_style)
    ws.write(row_num + 2, 7, number_format(total_pre_amount_with_vat),
             font_style)
    ws.write(row_num + 2, 8, number_format(total_pre_amount_ua), font_style)
    ws.write(row_num + 2, 9, number_format(total_pre_amount_with_vat_ua),
             font_style)

    ws.write(row_num + 2, 11, number_format(total_ord_amount), font_style)
    ws.write(row_num + 2, 12, number_format(total_ord_amount_with_vat),
             font_style)
    ws.write(row_num + 2, 13, number_format(total_ord_amount_ua), font_style)
    ws.write(row_num + 2, 14, number_format(total_ord_amount_with_vat_ua),
             font_style)

    wb.save(response)
    return response


@login_required
def excel_create(request, order_id):
    response = HttpResponse(content_type='application/ms-excel')
    options = str(f'attachment; filename=WebOrder_{order_id}_AstraLTD.xls')

    response['Content-Disposition'] = options

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [str(_('Attribute')), str(_('Value'))]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    order = Order.objects.select_related('user', 'template', 'company', 'stock',
                                         'signatory_of_documents',
                                         'VIN_code').get(
        pk=order_id)

    vat_rate = settings.VAT_RATE
    updated = order.updated

    if order.status == 'order':
        confirmation_date = updated
        rate = order.rate

    elif order.status == 'draft':

        confirmation_date = datetime.now()
        formatted_date = format_date(confirmation_date)

        # Кушування курсу євро НБУ
        cache_key = f"{formatted_date}_euro_exchange_rate"

        rate = cache.get(cache_key)
        if not rate:
            rate = get_euro_exchange_rate(formatted_date)
            cache.set(cache_key, rate, 60 * 60)

    fields = [
        (str(_('Status')), order.status),
        (str(_('WEB-order number')), order_id),
        (str(_('Created')), order.created.strftime(
            '%Y.%m.%d') if order.created else None),
        (str(_('Updated')), order.updated.strftime(
            '%Y.%m.%d') if order.updated else None),
        (str(_('Exchange rate date')), confirmation_date.strftime(
            '%Y.%m.%d') if confirmation_date else None),
        (str(_('Rate (€)')), rate if rate else None),
        (str(_('User')), order.user.username if order.user else None),
        (str(_('First and last name')),
         order.first_and_last_name if order.first_and_last_name else None),
        ('Email', order.email if order.email else None),
        (str(_('Company')), order.company.name if order.company else None),
        (str(_('edrpou code')), order.edrpou_code),
        (str(_('Formed')), order.formed if order.formed else None),
        (str(_('Stock')), order.stock.name if order.stock else None),
        (str(_('Signatory of documents')),
         order.signatory_of_documents.get_full_name() if order.signatory_of_documents else None),
        (str(_('VIN code')),
         order.VIN_code.serial_number if order.VIN_code else None),
        (str(_('Address')), order.address if order.address else None),
        (str(_('Services description')), order.services_description),
        (str(_('Comments')), order.comments),
    ]

    for field_num, field_value in enumerate(fields, start=1):
        ws.write(field_num, 0, field_value[0],
                 font_style)  # Записуємо назву поля в колонку "Поле".
        ws.write(field_num, 1, field_value[1],
                 font_style)  # Записуємо значення в колонку "Значення".

        # Записуємо інформацію про кожний OrderItem.
    row_num += len(
        fields) + 2  # Переміщуємось на наступний рядок після полів замовлення.

    order_items = order.items.all()  # Отримуємо всі OrderItem для даного замовлення.

    if order.status == 'order':
        order_item_columns = ['№', str(_('Category')), str(_('Product')),
                              str(_('Description')), str(_('Price (€)')),
                              str(_('Ord quantity')),
                              str(_('Ord cost (€) without VAT')),
                              str(_('Ord cost (€) with VAT')),
                              str(_('Ord cost (₴) without VAT')),
                              str(_('Ord cost (₴) with VAT'))]

        for col_num, col_value in enumerate(order_item_columns):
            ws.write(row_num, col_num, col_value, font_style)

        # Записуємо інформацію про кожний OrderItem.

        total_ord_amount = 0
        total_ord_amount_with_vat = 0
        total_ord_amount_ua = 0
        total_ord_amount_with_vat_ua = 0

        for index, order_item in enumerate(order_items, start=1):
            if order_item.ord_quantity > 0:  # В таб частину потрапляють лише замовлені товари
                row_num += 1
                ws.write(row_num, 0, index, font_style)
                ws.write(row_num, 1, order_item.product.category.name,
                         font_style)
                ws.write(row_num, 2, order_item.product.name, font_style)
                ws.write(row_num, 3, order_item.product.description, font_style)
                ws.write(row_num, 4,
                         number_format(order_item.price, decimal_pos=2),
                         font_style)
                ws.write(row_num, 5, number_format(order_item.ord_quantity),
                         font_style)
                ws.write(row_num, 6, number_format(
                    order_item.price * order_item.ord_quantity, decimal_pos=2),
                         font_style)
                ws.write(row_num, 7, number_format(
                    order_item.price * order_item.ord_quantity * vat_rate,
                    decimal_pos=2), font_style)
                ws.write(row_num, 8, number_format(
                    order_item.price * order_item.ord_quantity * rate,
                    decimal_pos=2), font_style)
                ws.write(row_num, 9, number_format(
                    order_item.price * order_item.ord_quantity * vat_rate * rate,
                    decimal_pos=2), font_style)

                total_ord_amount += order_item.price * order_item.ord_quantity
                total_ord_amount_with_vat += round(
                    order_item.price * order_item.ord_quantity * vat_rate, 2)
                total_ord_amount_ua += round(
                    order_item.price * order_item.ord_quantity * rate, 2)
                total_ord_amount_with_vat_ua += round(
                    order_item.price * order_item.ord_quantity * vat_rate * rate,
                    2)

            # Записуємо загальні суми.
        ws.write(row_num + 2, 5, str(_('Total')), font_style)

        ws.write(row_num + 2, 6, number_format(total_ord_amount), font_style)
        ws.write(row_num + 2, 7, number_format(total_ord_amount_with_vat),
                 font_style)
        ws.write(row_num + 2, 8, number_format(total_ord_amount_ua), font_style)
        ws.write(row_num + 2, 9, number_format(total_ord_amount_with_vat_ua),
                 font_style)



    elif order.status == 'draft':
        order_item_columns = ['№', str(_('Category')), str(_('Product')),
                              str(_('Description')), str(_('Price (€)')),
                              str(_('Pre quantity')),
                              str(_('Pre cost (€) without VAT')),
                              str(_('Pre cost (€) with VAT')),
                              str(_('Pre cost (₴) without VAT')),
                              str(_('Pre cost (₴) with VAT'))]

        for col_num, col_value in enumerate(order_item_columns):
            ws.write(row_num, col_num, col_value, font_style)

        # Записуємо інформацію про кожний OrderItem.

        total_pre_amount = 0
        total_pre_amount_with_vat = 0
        total_pre_amount_ua = 0
        total_pre_amount_with_vat_ua = 0

        for index, order_item in enumerate(order_items, start=1):
            row_num += 1
            ws.write(row_num, 0, index,
                     font_style)  # Записуємо номер рядка (індекс) OrderItem.
            ws.write(row_num, 1, order_item.product.category.name,
                     font_style)
            ws.write(row_num, 2, order_item.product.name, font_style)
            ws.write(row_num, 3, order_item.product.description, font_style)
            ws.write(row_num, 4,
                     number_format(order_item.price, decimal_pos=2),
                     font_style)
            ws.write(row_num, 5, number_format(order_item.pre_quantity),
                     font_style)
            ws.write(row_num, 6,
                     number_format(
                         order_item.price * order_item.pre_quantity,
                         decimal_pos=2), font_style)
            ws.write(row_num, 7, number_format(
                order_item.price * order_item.pre_quantity * vat_rate,
                decimal_pos=2),
                     font_style)
            ws.write(row_num, 8, number_format(
                order_item.price * order_item.pre_quantity * rate,
                decimal_pos=2),
                     font_style)
            ws.write(row_num, 9, number_format(
                order_item.price * order_item.pre_quantity * vat_rate * rate,
                decimal_pos=2),
                     font_style)

            total_pre_amount += order_item.price * order_item.pre_quantity
            total_pre_amount_with_vat += round(
                order_item.price * order_item.pre_quantity * vat_rate, 2)
            total_pre_amount_ua += round(
                order_item.price * order_item.pre_quantity * rate, 2)
            total_pre_amount_with_vat_ua += round(
                order_item.price * order_item.pre_quantity * vat_rate * rate,
                2)

            # Записуємо загальні суми.
        ws.write(row_num + 2, 5, str(_('Total')), font_style)
        ws.write(row_num + 2, 6, number_format(total_pre_amount), font_style)
        ws.write(row_num + 2, 7, number_format(total_pre_amount_with_vat),
                 font_style)
        ws.write(row_num + 2, 8, number_format(total_pre_amount_ua), font_style)
        ws.write(row_num + 2, 9, number_format(total_pre_amount_with_vat_ua),
                 font_style)

    wb.save(response)

    return response
