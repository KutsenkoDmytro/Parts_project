from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from customer.models import Holding, Company, Stock, Employee


class UserRole(models.Model):
    '''Визначає ролі, які можуть бути призначені користувачам.'''
    name = models.CharField(max_length=64, blank=True, default=None,
                            verbose_name=_('role name'))
    is_deleted = models.BooleanField(default=False,
                                     verbose_name=_('is_deleted'))
    date_added = models.DateTimeField(
        auto_now_add=True, verbose_name=_('date added'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'User role'
        verbose_name_plural = 'User roles'


class Profile(models.Model):
    '''Визначає додаткову інформацію про користувача.'''
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                verbose_name=_('user'))
    holding = models.ForeignKey(Holding, related_name='profiles',
                                on_delete=models.PROTECT, null=True,
                                verbose_name=_('holding'))

    role = models.ForeignKey(UserRole, related_name='profiles_user_role',
                             on_delete=models.PROTECT, null=True,
                             verbose_name=_('role'))

    position = models.CharField(max_length=100, verbose_name=_('position'))

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)


class UserCompany(models.Model):
    '''Визначає зв'язок між користувачами та компаніями.'''
    profile = models.ForeignKey(Profile,
                                on_delete=models.CASCADE,
                                verbose_name=_('profile'))

    company = models.ForeignKey(Company, related_name='users_companies',
                                on_delete=models.CASCADE,
                                verbose_name=_('company'))
    is_deleted = models.BooleanField(default=False,
                                     verbose_name=_('is_deleted'))

    def company_id(self):
        return self.id

    class Meta:
        ordering = ('company',)
        verbose_name = 'user company'
        verbose_name_plural = "user's company"
        unique_together = ('profile', 'company')

    def __str__(self):
        return str(self.company)


class OrderItemTemplate(models.Model):
    '''Визначає набори реквізитів для замовлень користувачів.'''
    name = models.CharField(max_length=200, verbose_name=_('template name'))

    user_company = models.ForeignKey(UserCompany,
                                     related_name='orders_item_templates_user_company',
                                     on_delete=models.CASCADE,
                                     verbose_name=_('user company'))

    stock = models.ForeignKey(Stock, related_name='orders_item_templates_stock',
                              on_delete=models.CASCADE, verbose_name=_('stock'))

    responsible_person = models.ForeignKey(Employee,
                                           related_name='orders_item_templates_employee',
                                           on_delete=models.CASCADE,
                                           verbose_name=_('responsible person'))

    address = models.TextField(max_length=300, verbose_name=_('adress'))
    is_deleted = models.BooleanField(default=False,
                                     verbose_name=_('is_deleted'))
    date_added = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('date added'))


    class Meta:
        ordering = ('name',)
        verbose_name = 'order item template'
        verbose_name_plural = 'order item templates'


    def __str__(self):
        return self.name
