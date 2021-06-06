from django.urls import path
from .views import *


urlpatterns = [
    path('profile', profile, name='profile'),
    path('register', register, name='register'),
    path('auth/login', login, name='login'),
    path('auth/logout', logout, name='logout'),
    path('profile/address', user_address, name='user_address'),
    path('auth/delete-user', delete_user, name='delete_user'),
    path('auth/token-refresh', refresh_token, name='refresh_token'),
    path('cart', cart_view, name='user-cart'),
    path('orders', orders_view, name='user-orders'),
    path('cart/add-to-cart', add_to_cart, name='user-orders'),
    path('cart/remove-from-cart', remove_from_cart, name='user-orders'),
    path('cart/change-cart-product-quantity', change_cart_product_quantity, name='user-orders'),
    path('cart/payment-method', cart_paymentMethod, name='user-orders'),
    path('cart/place-order', place_order, name='user-orders'),
]
