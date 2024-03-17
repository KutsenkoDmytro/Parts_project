from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _

from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from orders.functions import get_url_astra_shop

@login_required
@require_POST
def cart_add(request, product_id):
    '''Обробник для додавання товарів до кошика.'''
    cart = Cart(request, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data

        # Перевірка, чи кількість номенклатур у кошику не перевищує 100.
        product_limit = 100

        if cart.count_unique_items() >= product_limit:
            ms_part_1 = _('Your cart has reached the maximum limit in')
            ms_part_2 = _('products. Please proceed to checkout (drafts) or empty your cart!')

            messages.error(request, f"{ms_part_1} {product_limit} {ms_part_2}")
            return redirect('cart:cart_detail')

        cart.add(product=product,
                 quantity=cd['quantity'],
                 update_quantity=True)  # <-- Тут потрібно замінити значення cd['update']) на True.

    return redirect('cart:cart_detail')

@login_required
def cart_remove(request, product_id):
    '''Обробник для видалення товару з кошика.'''
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

@login_required
def cart_detail(request):
    '''Відображення вмісту кошика користувача.'''
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'],
                     'update': True})
    return render(request, 'cart/detail.html', {'cart': cart, 'url_astra_shop':get_url_astra_shop()})



