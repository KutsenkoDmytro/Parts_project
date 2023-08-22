from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('get_all_order_header_options/', views.get_all_order_header_options,
         name='get_all_order_header_options'),
    path('get_template_order_header_options/',
         views.get_template_order_header_options,
         name='get_template_order_header_options'),
    path('get_stock_options/', views.get_stock_options,
         name='get_stock_options'),
    path('get_signatory_of_documents_options/',
         views.get_signatory_of_documents_options,
         name='get_signatory_of_documents_options'),
    path('create/', views.order_create, name='order_create'),
    path('create_draft/', views.draft_order_create, name='draft_order_create'),
    # Вивід всіх замовлень.
    path('orders/', views.orders, name='orders'),
    # Сторінка для редагування замовлення.
    path('edit_order/<int:order_id>/', views.edit_order, name='edit_order'),
    # Сторінка для вивантаження замовлення в excel.
    path('excel_create/<int:order_id>/', views.excel_create, name='excel_create'),
    # Сторінка для вивантаження замовлення (детально) в excel.
    path('excel_detail/<int:order_id>/', views.excel_detail, name='excel_detail'),
]
