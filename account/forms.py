from django import forms
from django.forms import inlineformset_factory

from django.contrib.auth.models import User
from .models import Profile, UserCompany, Stock, Company, OrderItemTemplate, \
    Employee


class LoginForm(forms.Form):
    '''Форма для авторизації користувача.'''
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    '''Модельна форма для реєстрації користувача.'''
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    '''Форма дозволяє користувачам змінювати ім'я, прізвище, електронну пошту для вбудованої в Django моделі.'''

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    '''Форма дозволяє користувачу змінювати додаткову інформацію, яка зберігається в моделі профілю.'''

    class Meta:
        model = Profile
        fields = ('holding', 'role', 'position',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Перевіряємо, чи зберігається посилання на об'єкт вперше.
            self.fields['holding'].disabled = True
            self.fields['role'].disabled = True


class UserCompanyForm(forms.ModelForm):
    '''Форма дозволяє змінювати додаткову інформацію про підприємства користувача, яку ми зберігаємо в моделі профілю.'''

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        '''Визначає правила та обмеження для полів.'''

        # Початок блоку, що дозволяє вибирати компанії тільки по холдингу користувача.
        user_holding = Profile.objects.get(user=self.request.user).holding
        user_company_queryset = Company.objects.filter(holding=user_holding,
                                                       is_deleted=False)

        self.fields['company'].queryset = user_company_queryset
        # Кінець блоку, що дозволяє вибирати компанії тільки по холдингу користувача.

        # Заборона редагування компаній для існуючих екземплярів UserCompany.
        instance = kwargs.get('instance')
        if instance and instance.pk:
            self.fields['company'].disabled = True

    class Meta:
        model = UserCompany
        fields = ['company', ]


# Пов'язує моделі Profile та UserCompany.
ProfileItemFormSet = inlineformset_factory(Profile, UserCompany,
                                           form=UserCompanyForm,
                                           extra=0,
                                           can_delete=False)  # extra=1 якщо дозволяємо користувачу додавати компанії самостійно.


class CreateOrderItemTemplateForm(forms.ModelForm):
    '''Форма дозволяє користувачам редагувати свої шаблони замовлень.'''

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        '''Визначає правила та обмеження для полів.'''

        user_company_queryset = UserCompany.objects.filter(
            profile__user=self.request.user, is_deleted=False)

        # Перевірка помітки екземплярів на видалення.
        try:
            company_queryset = Company.objects.filter(
                users_companies__in=user_company_queryset)
        except UserCompany.DoesNotExist:
            company_queryset = {}

        try:
            stock_queryset = Stock.objects.filter(
                company__in=company_queryset)
        except Stock.DoesNotExist:
            stock_queryset = {}

        try:
            responsible_person_queryset = Employee.objects.filter(
                stocks_employee__in=stock_queryset).distinct()
        except Employee.DoesNotExist:
            stock_queryset = {}

        self.fields['user_company'].queryset = user_company_queryset
        self.fields['stock'].queryset = stock_queryset
        self.fields['responsible_person'].queryset = responsible_person_queryset

    class Meta:
        model = OrderItemTemplate
        fields = (
            'name', 'user_company', 'stock', 'responsible_person', 'address'
        )
