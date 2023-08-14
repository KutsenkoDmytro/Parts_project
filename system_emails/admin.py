from django.contrib import admin
from .models import EmailType,EmailSendingFact

# Register your models here.

admin.site.register(EmailType)



class EmailSendingFactAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EmailSendingFact._meta.fields]
    list_filter = ['email', 'type__name']
    search_fields = ['email', 'type__name','order__id','created','updated']

    class Meta:
        model = EmailSendingFact

admin.site.register(EmailSendingFact, EmailSendingFactAdmin)