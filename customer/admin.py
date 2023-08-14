from django.contrib import admin
from .models import Holding, Company, Stock, Employee, TechniqueType, Technique


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date_added']
    list_filter = ['name']
    search_fields = ['id', 'name', 'date_added']
    ordering = ['-id']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'edrpou_code', 'holding', 'is_deleted',
                    'date_added']
    list_filter = ['name', 'holding']
    search_fields = ['id', 'name', 'edrpou_code', 'holding__name', 'date_added']
    ordering = ['-id']


@admin.register(Employee)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'middle_name',
                    'company', 'position', 'is_deleted', 'date_added']
    list_filter = ['company', 'position']
    search_fields = ['id', 'last_name', 'first_name', 'middle_name',
                     'company__name', 'position', 'is_deleted', 'date_added']
    ordering = ['-id']


@admin.register(Stock)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'company', 'responsible_person', 'is_deleted',
                    'date_added']
    list_filter = ['company', 'responsible_person']
    search_fields = ['id', 'name', 'company__name',
                     'responsible_person__last_name', 'is_deleted',
                     'date_added']
    ordering = ['-id']


@admin.register(TechniqueType)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date_added']
    search_fields = ['id', 'name', 'date_added']
    ordering = ['-id']


@admin.register(Technique)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id','serial_number','company',  'technique_type',
                    'is_deleted','date_added']
    list_filter = ['company', 'technique_type']
    search_fields = ['id','serial_number','company__name',  'technique_type',
                    'is_deleted','date_added']
    ordering = ['-id']