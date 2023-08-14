# django-summernote
from django.contrib import admin
from .models import *
from django_summernote.admin import SummernoteModelAdmin


# Register your models here.

class PrivacyPolicyAdmin(SummernoteModelAdmin):
    list_display = [field.name for field in PrivacyPolicy._meta.fields]

    class Meta:
        model = PrivacyPolicy


admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)


class DocumentationAdmin(SummernoteModelAdmin):
    list_display = [field.name for field in Documentation._meta.fields]

    class Meta:
        model = Documentation


admin.site.register(Documentation, DocumentationAdmin)


class ContactAdmin(SummernoteModelAdmin):
    list_display = [field.name for field in Contact._meta.fields]

    class Meta:
        model = Contact


admin.site.register(Contact, ContactAdmin)


class MainEntryAdmin(SummernoteModelAdmin):
    list_display = [field.name for field in MainEntry._meta.fields]

    class Meta:
        model = Entry


admin.site.register(MainEntry, MainEntryAdmin)


class EntryAdmin(SummernoteModelAdmin):
    list_display = [field.name for field in Entry._meta.fields]

    class Meta:
        model = Entry


admin.site.register(Entry, EntryAdmin)
