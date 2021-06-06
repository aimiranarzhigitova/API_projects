from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class MadeIn(models.Model):
    country = models.CharField("Страна", max_length=30)
    description = models.TextField(blank=True, verbose_name='Описание')
    Developed = models.CharField("Разработали", max_length=50)
    date = models.DateField(verbose_name='Дата Изготовления')


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Vaccine(models.Model):
    category = models.ForeignKey(Category, verbose_name='Виды', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    ip = models.CharField(max_length=50, verbose_name='Определение')
    country = models.ForeignKey(MadeIn, verbose_name='Страна', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('vaccine_detail', kwargs={'slug': self.slug})

    def get_features(self):
        return {f.feature.feature_name: ' '.join([f.value, f.feature.unit or ""]) for f in self.features.all()}


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_order')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)


class Review(models.Model):
    name = models.CharField("Имя", max_length=100)
    text = models.TextField("Отзыв", max_length=500)
    parent = models.ForeignKey(
        'self', verbose_name='Родитель', on_delete=models.SET_NULL, blank=True, null=True
    )
    vaccine = models.ForeignKey(Vaccine, verbose_name='Вакцина', on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return f'{self.name} - {self.vaccine}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Voice(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE)
    voice_record = models.FileField()


class Statistics(models.Model):
    country = models.CharField('Страны', max_length=200)
    vaccinations = models.TextField('Вакцинированные')
    infected = models.TextField('Зараженные')
    died = models.TextField('Умерло')
    alive = models.TextField('Живут')


