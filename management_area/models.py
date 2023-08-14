from django.db import models
from django.utils.translation import gettext_lazy as _


class TextContent(models.Model):

    text = models.TextField(verbose_name=_('content'))
    is_active = models.BooleanField(default=True, verbose_name=_('is_active'))
    created = models.DateTimeField(auto_now_add=True, auto_now=False,
                                   verbose_name=_('created'))
    updated = models.DateTimeField(auto_now_add=False, auto_now=True,
                                   verbose_name=_('updated'))

    class Meta:
        abstract = True


class PrivacyPolicy(TextContent):

    class Meta:
        verbose_name = "Privacy policy"
        verbose_name_plural = "Privacy policy"


class Documentation(TextContent):

    class Meta:
        verbose_name = "Documentation"
        verbose_name_plural = "Documentation"


class Contact(TextContent):

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

class MainEntry(TextContent):

    class Meta:
        verbose_name = "Main entry"
        verbose_name_plural = "Main entries"


class Entry(TextContent):

    class Meta:
        verbose_name_plural = 'Entries'

    def __str__(self):
        if len(self.text) > 50:
            return self.text[:50] + "..."
        else:
            return self.text

