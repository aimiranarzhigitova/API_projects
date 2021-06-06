from rest_framework import serializers
from .models import Details, Address


class DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details
        fields = ['id', 'email', 'username', 'phone', 'date_joined']


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = '__all__'
