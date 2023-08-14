from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class EmailType(models.Model):
    name = models.CharField(max_length=64, blank=True, default=None,verbose_name=_('email type name'))
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('updated'))

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = 'Email type'
        verbose_name_plural = 'Types of emails'


class EmailSendingFact(models.Model):
    type = models.ForeignKey(EmailType, on_delete=models.CASCADE, verbose_name=_('type'))
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE,
                              blank=True, null=True,
                              default=None, verbose_name=_('order'))  # if mail is related to any order
    email = models.EmailField(verbose_name=_('email'))  # to vhom email
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('updated'))

    def __str__(self):
        return str(self.type)

    class Meta:
        verbose_name = 'Sent email'
        verbose_name_plural = 'Emails sent'

