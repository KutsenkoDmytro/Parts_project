from django.db import models
from django.urls import reverse
from django_currentuser.middleware import (get_current_user,
                                           get_current_authenticated_user)
from django.utils.translation import gettext_lazy as _

from customer.models import Holding
from account.models import Profile



class Category(models.Model):
    '''Опис категорій товарів.'''
    name = models.CharField(max_length=200, db_index=True,
                            verbose_name=_('category name'))
    slug = models.SlugField(max_length=200, unique=True,
                            verbose_name=_('category slug'))

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    '''Опис товарів.'''
    category = models.ForeignKey(Category,
                                 related_name='products',
                                 on_delete=models.CASCADE,
                                 verbose_name=_('category'))
    name = models.CharField(max_length=200, db_index=True,
                            verbose_name=_('product name'))
    slug = models.SlugField(max_length=200, db_index=True,
                            verbose_name=_('product slug'))
    axial = models.CharField(max_length=14, blank=True, default='',
                             verbose_name='axial')
    cross_number = models.TextField(db_index=True, blank=True, default='',
                            verbose_name=_('cross number'))

    # image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True,
                                   verbose_name=_('description'))
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name=_('price'))
    # available = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False,
                                     verbose_name=_('is deleted'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))


    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])

    def get_price_with_coefficient(self, user):
        '''Отримання ціни з коефіцієнтом.'''

        user_profile = Profile.objects.get(user=get_current_user())
        coefficient = Coefficient.objects.get(category=self.category,
                                              holding=user_profile.holding)
        price_with_coefficient = self.price * coefficient.value
        return round(price_with_coefficient, 2)

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name


class Coefficient(models.Model):
    category = models.ForeignKey(Category, related_name='coefficients_category',
                                 on_delete=models.CASCADE,
                                 verbose_name=_('category'))
    holding = models.ForeignKey(Holding, related_name='coefficients_holding',
                                on_delete=models.CASCADE,
                                verbose_name=_('holdind'))
    value = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name=_('value'))
    is_deleted = models.BooleanField(default=False,
                                     verbose_name=_('is deleted'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))

    class Meta:
        verbose_name = 'coefficient'
        verbose_name_plural = 'coefficients'

    def __str__(self):
        return f'Coefficient for {self.category} - {self.holding}'
