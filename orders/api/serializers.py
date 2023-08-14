from rest_framework import serializers
from ..models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    class Meta:
        model = OrderItem
        fields = ['id','order','product','price','pre_quantity','ord_quantity']

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    company = serializers.StringRelatedField()
    stock = serializers.StringRelatedField()
    signatory_of_documents = serializers.StringRelatedField()


    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'status', 'user',
                    'company', 'edrpou_code', 'first_and_last_name',
                    'email', 'formed', 'stock',
                    'signatory_of_documents', 'address',
                    'services_description', 'comments', 'VIN_code', 'rate',
                    'created', 'updated','items'
                    ]


