from rest_framework.serializers import ModelSerializer
from .models import *


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductDetailSerializer(ModelSerializer):
    class Meta:
        model = ProductDetails
        fields = '__all__'


class QuantityProductSerializer(ModelSerializer):
    class Meta:
        model = QuantityProduct
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'
