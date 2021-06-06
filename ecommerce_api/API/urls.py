from django.urls import path
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^products/$', products_view, name='products'),
    url(r'^products/pdns/$', product_detailed_view, name='product'),
    url(r'^product/create/$', create_product, name='create_product'),
    url(r'^product/update/$', update_product, name='update_product'),
    url(r'^product/delete/$', delete_product, name='delete_product'),
]
