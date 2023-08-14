from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, Coefficient

from  import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'slug']
    search_fields = ['id','name', 'slug']
    ordering = ['-id']
    prepopulated_fields = {'slug': ('name',)}

class ProductResource(resources.ModelResource):
    category = fields.Field(column_name='category', attribute='category', widget=ForeignKeyWidget(Category,'name'))

    class Meta:
        model = Product

@admin.register(Product)
class ProductAdmin(ImportExportActionModelAdmin):
    resource_class = ProductResource
    list_display = list_display = ['id','name','slug','description', 'price','category', 'is_deleted', 'created', 'updated']
    list_filter = ['category']
    list_editable = ['price']
    ordering = ['-id']
    prepopulated_fields = {'slug': ('name',)}

#@admin.register(Product)
#class ProductAdmin(admin.ModelAdmin):
#    list_display = ['name', 'is_deleted','slug','description', 'price', 'created', 'updated']
#    list_filter = [ 'created', 'updated']
#    list_editable = ['price']
#    prepopulated_fields = {'slug': ('name',)}


@admin.register(Coefficient)
class CoefficientAdmin(admin.ModelAdmin):
    list_display = ['id','category','holding','value','is_deleted', 'created', 'updated']
    list_filter = ['category','holding']
    list_editable = ['value']
    ordering = ['-id']
