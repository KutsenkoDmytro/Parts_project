from rest_framework import generics
from ..models import Order
from .serializers import OrderSerializer
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets



class OrderListView(generics.ListAPIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderDetailView(generics.RetrieveAPIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
