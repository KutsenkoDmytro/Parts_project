from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('orders', views.OrderViewSet)

app_name = 'orders'
urlpatterns = [
    path('v1/orders/',
         views.OrderListView.as_view(),
         name='order_list'),
    path('v1/orders/<pk>/',
         views.OrderDetailView.as_view(),
         name='order_detail'),
    path('v1/', include(router.urls)),
]
