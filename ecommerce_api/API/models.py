import uuid
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from user.models import Details, Address


class Product(models.Model):
    productId = models.AutoField(primary_key=True)
    name = models.CharField(help_text='Name of product', max_length=200)
    productSlug = models.SlugField(max_length=500, default='', unique=True)
    price = models.PositiveBigIntegerField(help_text='Price of Product', default=0)
    manufacturer = models.CharField(help_text='Name of manufacturer', max_length=200, default='')
    thumbnail = models.CharField(help_text='Paste link of thumbnail photo', max_length=300, default='', blank=True)
    stock = models.PositiveBigIntegerField(help_text='Available quantity of product', default=0)
    isInStock = models.BooleanField(help_text='is product available for purchases?', default=False)
    paymentOption = models.CharField(help_text="What's the payment options available on product", max_length=300,
                                     default='Cash On Delivery (C.O.D.)')

    def __str__(self):
        return f"{self.productId}) {self.name}"


class ProductDetails(models.Model):
    product_id = models.OneToOneField(Product, help_text='Select product ID', on_delete=models.CASCADE,
                                      primary_key=True)
    brand = models.CharField(max_length=200, default=None, null=True)
    description = models.TextField(help_text='Description of the product', default='')
    countryOfOrigin = models.CharField(help_text="What's the Country of Origin", max_length=20, default=None)
    photos = ArrayField(models.CharField(max_length=450, default=None), blank=True, default=None,
                        help_text="Paste links for the photos of products separated by commas")
    categories = ArrayField(models.CharField(max_length=20, default=None), blank=True, default=None,
                            help_text="Define category of product")
    rating = models.DecimalField(decimal_places=1, max_digits=5, blank=True, help_text="rating out of 5")
    discount = models.DecimalField(decimal_places=2, max_digits=12, blank=True,
                                   help_text="how much discount is ongoing for product (in %)")
    coupons = ArrayField(models.CharField(max_length=20, default=None), default=None, blank=True,
                         help_text="coupon codes for this product separated by commas")

    def __str__(self):
        return f"{self.product_id.productId} - {self.product_id.name}"


class QuantityProduct(models.Model):
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    prod_quantity = models.PositiveIntegerField(null=True)


class Order(models.Model):
    orderId = models.UUIDField(auto_created=True, default=uuid.uuid4, unique=True)
    orderState = models.CharField(max_length=15, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    userId = models.ForeignKey(Details, on_delete=models.CASCADE, null=True)
    paymentMethod = models.CharField(max_length=20, null=True)
    finalAmount = models.CharField(max_length=80, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    products = models.ManyToManyField(QuantityProduct)


class Cart(models.Model):
    products = models.ManyToManyField(QuantityProduct)
    userId = models.OneToOneField(Details, on_delete=models.CASCADE, null=True)
    paymentMethod = models.CharField(max_length=20, null=True)
    finalAmount = models.CharField(max_length=80, null=True)
    # products = models.ManyToManyField(Product)
