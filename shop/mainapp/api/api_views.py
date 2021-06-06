from collections import OrderedDict

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.generics import ListAPIView,  ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from .serializers import RegisterSerializer, UserSerializer, CategorySerializer, BaseProductSerializer, CustomerSerializer, CartProductSerializer, CartSerializers, OrderSerializer
from ..models import Category, Product, Customer, CartProduct, Cart, Order
from knox.models import AuthToken



# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": UserSerializer (user, context=self.get_serializer_context()).data,
        "token": AuthToken.objects.create(user)[1]
        })



class ProductPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 60

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('objects_count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('items', data)
        ]))


class CategoryListApiView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class CategoryApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class ProductListApiView(ListCreateAPIView):
    serializer_class = BaseProductSerializer
    pagination_class = ProductPagination
    queryset = Product.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['ip']


class ProductDetailApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = BaseProductSerializer
    queryset = Product.objects.all()


class CustomersListApiView(ListAPIView):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


class CartProductListApiView(ListAPIView):
    serializer_class = CartProductSerializer
    queryset = CartProduct.objects.all()


class CartListApiView(ListAPIView):
    serializer_class = CartSerializers
    queryset = Cart.objects.all()


class OrderListApiView(ListAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()