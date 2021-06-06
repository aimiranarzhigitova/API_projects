from rest_framework import serializers
from .models import Category, Vaccine, Customer, Review, MadeIn, Voice, Statistics


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    slug = serializers.SlugField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug'
        ]


class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = "__all__"


class MadeInSerializers(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    slug = serializers.SlugField()

    class Meta:
        model = MadeIn
        fields = "__all__"


class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = '__all__'


class ReviewCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('name', 'text', 'parent')


class BaseVaccineSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects, slug_field='name')
    title = serializers.CharField(required=True)
    slug = serializers.SlugField(required=True)
    image = serializers.ImageField(required=True)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=9, decimal_places=2, required=True)
    reviews = ReviewCreateSerializers(many=True)

    class Meta:
        model = Vaccine
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
