from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from utils.uploadings import UploadingProducts, UploadingCart
from django.contrib import messages
from django.core.paginator import Paginator
from utils.rates import get_current_euro_exchange_rate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from management_area.models import Entry, MainEntry
from django.db.models import Max, Q
from django.utils.translation import gettext_lazy as _
from django.http import Http404

from .models import Category, Product, Coefficient,Profile
from orders.functions import get_time_until_end_of_day
from cart.forms import CartAddProductForm
from cart.cart import Cart
import traceback
from orders.functions import get_url_astra_shop



@login_required
def index(request):
    '''Обробник доманшьої сторінки.'''
    entries = Entry.objects.filter(is_active=True).order_by('-created')
    latest_main_entry = MainEntry.objects.filter(is_active=True).aggregate(
        latest_created=Max('created'))['latest_created']

    if latest_main_entry is not None:
        main_entry = MainEntry.objects.get(is_active=True,
                                           created=latest_main_entry)
        return render(request, 'shop/index.html',
                      {'main_entry': main_entry, 'entries': entries})
    else:
        # Обробка, якщо не знайдено жодного активного MainEntry.
        return render(request, 'shop/index.html',
                      {'main_entry': None, 'entries': entries})


@login_required

def product_search(request):
    '''Обробляє пошуковий запит і відображає результати.'''
    query_search = request.GET.get('search')
    query_category = request.GET.get('category')
    user = request.user

    products = Product.objects.filter(is_deleted=False)

    if query_search:
        products = products.filter(Q(name__contains=query_search) | Q(cross_number__contains=query_search))

    if query_category:
        products = products.filter(category__slug=query_category)

    # Оптимізований запит для завантаження пов'язаної категорії для кожного продукту.
    products = products.select_related('category')

    categories = Category.objects.all()

    paginator = Paginator(products, 5)  # Показувати по 5 товарів на сторінці.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Отримуємо профіль користувача та коефіцієнти, для всіх продуктів на сторінці.

    user_profile = get_object_or_404(Profile, user=user)

    coefficients = Coefficient.objects.filter(
        category__in=[product.category for product in page_obj.object_list],
        holding=user_profile.holding
    ).select_related('category')

    # Створюємо словник коефіцієнтів за категоріями для подальшого використання у циклі.
    coefficient_by_category = {coefficient.category_id: coefficient for
                               coefficient in coefficients}

    # Кешування курсу євро НБУ.
    rate = cache.get('current_euro_exchange_rate')
    if not rate:
        rate = get_current_euro_exchange_rate()
        cache.set('current_euro_exchange_rate', rate, get_time_until_end_of_day())

    # Додаємо цикл, щоб обчислити price_coef для кожного продукту на сторінці.
    for product in page_obj.object_list:
        coefficient = coefficient_by_category.get(product.category_id)
        if coefficient:
            product.price_coef = round(product.price * coefficient.value, 2)
            product.price_ua = round(product.price_coef * rate, 2)
        else:
            raise Http404("Coefficient not found for product category.")

    return render(request, 'shop/product/search.html', {
        'query': query_search,
        'page_obj': page_obj,
        'categories': categories,
        'category': query_category,  # Передаємо обрану категорію у шаблон
        'url_astra_shop': get_url_astra_shop()
    })


@login_required
def product_detail(request, id, slug):
    '''Відображає товар з його детальним описом.'''
    product = get_object_or_404(Product, id=id, slug=slug)
    cart_product_form = CartAddProductForm()
    user = request.user
    product.price_coef = product.get_price_with_coefficient(user)

    # Кешування курсу євро НБУ
    rate = cache.get('current_euro_exchange_rate')
    if not rate:
        rate = get_current_euro_exchange_rate()
        cache.set('current_euro_exchange_rate', rate, get_time_until_end_of_day())

    product.price_ua = round(
        product.price_coef * rate, 2)
    return render(
        request,
        'shop/product/detail.html',
        {'product': product, 'cart_product_form': cart_product_form}
    )


def superuser_required(view_func):
    '''Функція, яка перевіряє, чи є поточний користувач суперюзером.'''
    return user_passes_test(lambda u: u.is_superuser)(view_func)


@superuser_required
def download_products(request):
    '''Обробник який дозволяє завантажувати нові товари в модель товари.'''
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, _('File not selected!'))
            return render(request,
                          'shop/product/download_products.html',
                          locals())
        try:
            file = request.FILES['file']
            uploading_file = UploadingProducts({'file': file})

            if uploading_file:
                messages.success(request, _('The download was successful!'))
            else:
                messages.error(request, _('Error loading!'))
        except Exception as e:
            # Вивести докладну інформацію про виняток у консолі та в логах помилок
            traceback.print_exc()
            messages.error(request, f'An error occurred: {str(e)}')
    return render(request, 'shop/product/download_products.html', locals())


@login_required
def download_products_in_cart(request):
    '''Обробник який дозволяє завантажувати нові товари в сесію, в корзину.'''
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, _('File not selected!'))
            return render(request,
                          'shop/product/download_products_in_cart.html',
                          locals())

        file = request.FILES['file']
        uploading_file = UploadingCart({'file': file})

        if uploading_file:
            result_dict = uploading_file.result_dict
            print(result_dict)
            limit_reached = False
            cart = Cart(request)
            items_in_cart = cart.count_unique_items()
            download_items = 0
            product_limit = 100

            for item in result_dict['data']:
                if items_in_cart + download_items >= product_limit:
                    limit_reached = True
                    break

                product = item['product']

                try:
                    quantity = int(item['quantity'])
                except ValueError:
                    quantity = 1  # якщо не вдалося перетворити на число, встановлюємо значення кількості за замовчуванням.

                cart.add(product=product, quantity=quantity)
                download_items += 1

            if limit_reached:
                ms_part_1 = _(
                    'Your cart has reached the maximum limit in')
                ms_part_2 = _('products. From file .xls downloaded')
                ms_part_3 = _('from')
                ms_part_4 = _('products')
                ms_part_5 = _(
                    'Please proceed to checkout (drafts) or empty your cart! ')
                error_message = f'{ms_part_1} {product_limit} {ms_part_2} {download_items} {ms_part_3} {len(result_dict["data"])} {ms_part_4}.\n {ms_part_5}'
                messages.error(request, error_message)
            else:
                messages.success(request,
                                 _('Products have been successfully added to your shopping cart!'))

        else:
            messages.error(request,
                           _('An error occurred while downloading the file!'))

    return render(request, 'shop/product/download_products_in_cart.html',
                  locals())


@login_required
def add_one_to_cart(request, product_id):
    '''Додає один товар до корзини.'''
    product = get_object_or_404(Product, id=product_id)
    quantity = 1

    cart = Cart(request)
    cart.add(product=product, quantity=quantity)

    return redirect(reverse('cart:cart_detail'))
