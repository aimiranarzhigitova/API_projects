from django.utils import timezone
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class Details(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=True, null=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    phone = models.CharField(max_length=14, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username'
    ]

    objects = UserManager()

    def __str__(self):
        return self.email


class Address(models.Model):
    HOME_ADDRESS = 'H'
    WORK_ADDRESS = 'W'
    ADDRESS_TYPES = [
        (HOME_ADDRESS, 'Home'),
        (WORK_ADDRESS, 'Work')
    ]
    userId = models.ForeignKey(Details, on_delete=models.CASCADE, null=True)
    area = models.CharField(max_length=50, null=True)
    landmark = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    pinCode = models.CharField(max_length=10, null=True)
    type = models.CharField(max_length=10, null=True)

    def __str__(self):
        area_str = ''
        if self.area and self.area != '':
            area_str = self.area
        if self.city and self.city != '':
            if area_str:
                area_str += ', ' + self.city
            else:
                area_str = self.city
        if self.country and self.country != '':
            if area_str:
                area_str += ', ' + self.country
            else:
                area_str = self.country
        return area_str if area_str else '(unavailable)'
