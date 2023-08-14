from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'user',
                    'company', 'edrpou_code', 'template', 'first_and_last_name',
                    'email', 'formed', 'stock',
                    'signatory_of_documents', 'address',
                    'services_description', 'comments', 'VIN_code', 'rate',
                    'created', 'updated'
                    ]
    list_filter = ['status', 'user', 'company']
    inlines = [OrderItemInline]
    search_fields = ['id', 'status', 'user__username',
                     'company__name', 'edrpou_code', 'template__name',
                     'first_and_last_name', 'email', 'formed', 'stock__name',
                     'signatory_of_documents__last_name', 'address',
                     'services_description', 'comments', 'VIN_code__serial_number', 'rate',
                     'created', 'updated']
    ordering = ['-id']
