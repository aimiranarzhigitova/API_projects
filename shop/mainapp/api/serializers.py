from rest_framework import serializers
from ..models import Category, Product, Customer, Order, CartProduct, Cart
from django.contrib.auth.models import User

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    slug = serializers.SlugField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug'
        ]


class BaseProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects, slug_field='name')
    title = serializers.CharField(required=True)
    slug = serializers.SlugField(required=True)
    image = serializers.ImageField(required=True)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=9, decimal_places=2, required=True)

    class Meta:
        model = Product
        fields = '__all__'


class CartProductSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Customer.objects)
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects, source="product.title")
    qty = serializers.IntegerField(required=True)
    final_price = serializers.DecimalField(max_digits=9, decimal_places=2, required=True)

    class Meta:
        model = CartProduct
        fields = '__all__'



class CartSerializers(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects, source="product.title")

    class Meta:
        model = Cart
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True)

    class Meta:
        model = Customer
        fields = '__all__'

