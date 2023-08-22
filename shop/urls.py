'''Визначає схеми URL для shop.'''
from django.urls import path,re_path
from . import views


app_name = 'shop'
urlpatterns = [
# Домашня сторінка
    # Домашня сторінка.
    path('', views.index, name='index'),
    path('product_search/', views.product_search, name='product_search'),
    path('download-products/', views.download_products, name='download_products'),
    path('download-products-in-cart/', views.download_products_in_cart, name='download_products_in_cart'),
    re_path(r'^(?P<id>\d+)/(?P<slug>[-a-zA-Z0-9_./]+)/$', views.product_detail, name='product_detail'),
    path('<slug:category_slug>/', views.product_search, name='product_list_by_category'),
    path('add_one_to_cart/<int:product_id>/', views.add_one_to_cart, name='add_one_to_cart'),
]
