from django.urls import path
from .api_views import RegisterAPI, CategoryListApiView, CategoryApiView, ProductListApiView,\
    ProductDetailApiView, CustomersListApiView, CartProductListApiView, CartListApiView, OrderListApiView

urlpatterns = [
    path('categories/', CategoryListApiView.as_view(), name='categories_list'),
    path('categories/<str:pk>/', CategoryApiView.as_view(), name='categories_detail'),
    path('customers/', CustomersListApiView.as_view(), name='customers_list'),
    path('products/', ProductListApiView.as_view(), name='products'),
    path('products/<str:pk>/', ProductDetailApiView.as_view(), name='products_detail'),
    path('cartproducts/', CartProductListApiView.as_view(), name='cart_products_list'),
    path('cart/', CartListApiView.as_view(), name='cart_list'),
    path('order/', OrderListApiView.as_view(), name='order_list'),
    path('api/register/', RegisterAPI.as_view(), name='register'),

]