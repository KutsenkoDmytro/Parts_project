from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.db import IntegrityError
from django.utils.translation import gettext as _


from .forms import LoginForm, UserRegistrationForm, UserEditForm, \
    ProfileEditForm, ProfileItemFormSet, CreateOrderItemTemplateForm
from .models import Profile, UserCompany, OrderItemTemplate, Stock, Company, \
    Employee


def user_login(request):
    '''Обробка входу користувача в акаунт.'''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponse('Authenticated successfully')
            else:
                return HttpResponse('Disabled account')
        else:
            return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    '''Сторінка на яку переходить користувач після успішного входу.'''
    return render(request, 'shop/shop/index.html', {'section': 'index'})


def register(request):
    '''Реєстрація нового користувача.'''
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Ми створюємо нового користувача, але поки не зберігаємо його в базу даних.
            new_user = user_form.save(commit=False)
            # Встановлюємо зашифрований пароль для користувача.
            new_user.set_password(user_form.cleaned_data['password'])
            # Зберігаємо користувача в базі даних.
            new_user.save()

            # Створення профілю користувача.
            Profile.objects.create(user=new_user)

            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required
def edit(request):
    '''Обробка змін, внесених користувачем в обліковий запис.'''
    user_profile = get_object_or_404(Profile,user=request.user)
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=user_profile,
                                       data=request.POST)
        profile_item_formset = ProfileItemFormSet(
            instance=request.user.profile,
            data=request.POST,
            form_kwargs={'request': request}
            # При звязуванні форм формсетом request передаємо form_kwargs={'request': request}
        )

        if user_form.is_valid() and profile_form.is_valid() and profile_item_formset.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            profile_item_formset.save()

            messages.success(request,
                             _('The profile has been successfully updated!'))
            return redirect('account:edit')
        else:
            messages.error(request, _('Error updating profile!'))

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=user_profile)
        user_companies = request.user.profile.usercompany_set.filter(
            is_deleted=False)

        profile_item_formset = ProfileItemFormSet(instance=request.user.profile,
                                                  queryset=user_companies,
                                                  form_kwargs={
                                                      'request': request})  # При звязуванні форм формсетом request передаємо form_kwargs={'request': request}

    return render(request, 'account/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile_item_formset': profile_item_formset
    })


class CreateOrderItemTemplate(CreateView):
    '''Створення нового набору реквізитів замовлення.'''
    model = OrderItemTemplate
    fields = ['name', 'user_company', 'stock', 'responsible_person', 'address']
    template_name = 'order_template/create.html'
    success_url = reverse_lazy('account:create_template')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        # Визначення списків варіантів для полів вводу.

        user_company_queryset = UserCompany.objects.filter(
            profile__user=self.request.user, is_deleted=False)

        company_queryset = Company.objects.filter(
            users_companies__in=user_company_queryset, is_deleted=False)

        stock_queryset = Stock.objects.filter(
            company__in=company_queryset, is_deleted=False)

        responsible_person_queryset = Employee.objects.filter(
            stocks_employee__in=stock_queryset, is_deleted=False).distinct()




        form.fields['user_company'].queryset = user_company_queryset
        form.fields['stock'].queryset = stock_queryset
        form.fields['responsible_person'].queryset = responsible_person_queryset

        return form

    def form_valid(self, form):
        '''Вивід повідомлення при успішному створенні екземпляру набору реквізитів замовлення.'''
        try:
            form.save()
            messages.success(self.request,
                             _('A new set of order details has been successfully created!'))
        except IntegrityError as e:
            return self.form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        '''
        Вивід повідомлення при помилці створення екземпляру набору реквізитів замовлення.
        '''
        response = super().form_invalid(form)
        error_message = form.errors['__all__'][
            0] if '__all__' in form.errors else _(
            'Error creating set of order details.')
        messages.error(self.request, error_message)
        return response

    def get_success_url(self):
        return reverse('account:template_list')




@login_required
def get_stock_options(request):
    '''
    Призначений для обробки AJAX-запиту та повернення JSON-відповіді із
    списком опцій для поля "stock" в залежності від обраного значення в полі "user_company".
    '''
    user_company_id = request.GET.get('user_company_id')
    user_company_obj = UserCompany.objects.get(id=user_company_id)
    company = user_company_obj.company

    try:
        stock_queryset = Stock.objects.filter(company=company, is_deleted=False)
        stock_options = {str(stock.id): stock.name for stock in stock_queryset}

    except Stock.DoesNotExist:
        stock_options = {}

    return JsonResponse({'stock_options': stock_options})


@login_required
def get_responsible_person_options(request):
    '''
    Призначений для обробки AJAX-запиту та повернення JSON-відповіді із
    списком опцій для поля "responsible_person" в залежності від обраних значень у полях
    "stock" та "user_company".
    '''

    stock_id = request.GET.get('stock')

    try:
        responsible_person = Employee.objects.get(
            stocks_employee__id=stock_id, is_deleted=False)

        responsible_person_options = {
            str(responsible_person.id): responsible_person.get_full_name()}
    except Employee.DoesNotExist:
        responsible_person_options = {}

    return JsonResponse(
        {'responsible_person_options': responsible_person_options})


@login_required
def template_list(request):
    '''Відображає список всіх наборів реквізитів замовлень користувача.'''

    # Здійснюємо оптимізований запит до бази даних.
    templates = OrderItemTemplate.objects.filter(
        user_company__profile__user=request.user, is_deleted=False
    ).order_by('date_added').select_related('user_company', 'stock',
                                            'responsible_person',
                                            'user_company__company')

    context = {'user_templates': templates}

    return render(request, 'order_template/template_list.html', context)


@login_required
def edit_template(request, template_id):
    '''Зміна набору реквізитів користувачем.'''
    template = get_object_or_404(
        OrderItemTemplate.objects.select_related('user_company', 'stock',
                                                 'responsible_person',
                                                 'user_company__profile__user'),
        pk=template_id)


    if request.method == 'POST':
        template_form = CreateOrderItemTemplateForm(request.POST,
                                                    instance=template,
                                                    request=request)

        if template_form.is_valid():
            template_form.save()

            # Перенаправлення на сторінку, якщо дія успішна.
            return HttpResponseRedirect(reverse('account:template_list'))

    else:
        template_form = CreateOrderItemTemplateForm(instance=template,
                                                    request=request)

    return render(request, 'order_template/edit.html', {
        'template': template,
        'template_form': template_form,
    })
