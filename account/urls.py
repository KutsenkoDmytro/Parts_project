from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from . import views

app_name = 'account'

urlpatterns = [
    # Обробники входу та виходу.
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Обробники зміни паролю.
    path('password_change/', auth_views.PasswordChangeView.as_view(
        success_url=reverse_lazy('account:password_change_done')),
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    # Обробники відновлення паролю.
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             email_template_name='registration/password_reset_email.html',
             success_url=reverse_lazy('account:password_reset_done')),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('account:password_reset_complete')),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    # Обробник реєстрації.
    path('register/', views.register, name='register'),
    # Обробник зміни інформації в профілі.
    path('edit/', views.edit, name='edit'),
    # Обробники створення нового набору реквізитів замовлення.
    path('get_stock_options/', views.get_stock_options, name='get_stock_options'),
    path('get_responsible_person_options/', views.get_responsible_person_options, name='get_responsible_person_options'),
    path('create_template/', views.CreateOrderItemTemplate.as_view(), name='create_template'),
    path('template_list/', views.template_list, name='template_list'),
    path('edit_template/<int:template_id>/',views.edit_template, name='edit_template'),
]
