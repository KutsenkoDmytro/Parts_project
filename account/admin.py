from django.contrib import admin
from .models import Profile, UserCompany,OrderItemTemplate,UserRole
from django.db.models import F


#class UserCompanyInline(admin.TabularInline):
#    model = UserCompany
#    raw_id_fields = ['profile']

@admin.register(UserCompany)
class UserCompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'profile', 'is_deleted']
    list_filter = ['company', 'profile','is_deleted']
    search_fields = ['id', 'company__name']
    ordering = ['-id']



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id','user','holding','role','position']
    list_filter = ['holding','position']
    #inlines = [UserCompanyInline]
    search_fields = ['id','user__username','role','holding__name','position']
    ordering = ['-id']

@admin.register(OrderItemTemplate)
class OrderItemTemplateAdmin(admin.ModelAdmin):
    list_display = ['id','owner','name','user_company','user_company_id','stock','responsible_person','address','is_deleted','date_added']
    list_filter = ['stock','responsible_person','is_deleted']
    search_fields = ['id','name','user_company__company__name', 'stock__name','responsible_person__last_name', 'address','date_added']
    ordering = ['-id']

    def owner(self, obj):
        return obj.user_company.profile.user

    owner.short_description = 'owner'
    def user_company_id(self, obj):
        return obj.user_company.id

    user_company_id.short_description = 'user company id'


@admin.register(UserRole)
class OrderItemTemplateAdmin(admin.ModelAdmin):
    list_display = ['id','name','is_deleted','date_added']
    search_fields = ['id','name','is_deleted','date_added']
    ordering = ['-id']
