from django.db import models


class Holding(models.Model):
    '''Визначає холдинг, який є батьківським суб'єктом для підприємств.'''

    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'holding'
        verbose_name_plural = 'holdings'

    def __str__(self):
        return self.name


class Company(models.Model):
    '''Визначає підприємство холдингу.'''

    holding = models.ForeignKey(Holding, related_name='companies_holding',
                                on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    edrpou_code = models.CharField(max_length=8)
    is_deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'company'
        verbose_name_plural = 'companies'
        unique_together = ('holding',
                           'name')# Унікальна комбінація в межах кожного холдингу.

    def __str__(self):
        return self.name


class Employee(models.Model):
    '''Визначає працівника підприємства.'''
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    company = models.ForeignKey(Company, related_name='employees_company',
                                on_delete=models.PROTECT)
    position = models.CharField(max_length=100)

    is_deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('last_name',)
        verbose_name = 'employee'
        verbose_name_plural = 'employees'
        unique_together = ('company', 'first_name', 'last_name',
                           'middle_name') # Унікальна комбінація в межах кожного працівника.

    def get_full_name(self):
        # Метод для отримання повного ім'я працівника.
        if self.middle_name:
            full_name = f"{self.last_name} {self.first_name} {self.middle_name}"
        else:
            full_name = f"{self.last_name} {self.first_name}"
        return full_name

    def __str__(self):
        if self.middle_name:
            full_name = f"{self.last_name} {self.first_name} {self.middle_name}"
        else:
            full_name = f"{self.last_name} {self.first_name}"
        return f"{full_name}"



class Stock(models.Model):
    '''Визначає склад підприємства.'''
    name = models.CharField(max_length=300)
    company = models.ForeignKey(Company, related_name='stocks_companies',
                                on_delete=models.PROTECT)
    responsible_person = models.ForeignKey(Employee,
                                           related_name='stocks_employee',
                                           on_delete=models.PROTECT)
    is_deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'stock'
        verbose_name_plural = 'stocks'
        unique_together = ('company',
                           'name')  # Унікальна комбінація в межах кажної компанії.

    def __str__(self):
        return self.name


class TechniqueType(models.Model):
    '''Визначає тип техніки.'''

    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'technique type'
        verbose_name_plural = 'technique types'

    def __str__(self):
        return self.name


class Technique(models.Model):
    '''Визначає техніку підприємства.'''

    technique_type = models.ForeignKey(TechniqueType, related_name='technique_technique_type',
                                       on_delete=models.PROTECT)
    company = models.ForeignKey(Company, related_name='technique_company',
                                on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('serial_number',)
        verbose_name = 'technique'
        verbose_name_plural = 'technique'

    def __str__(self):
        return self.serial_number
