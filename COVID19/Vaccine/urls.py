from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoryListApiView.as_view(), name='categories_list'),
    path('categories/<str:pk>/', CategoryApiView.as_view(), name='categories_detail'),
    path('customers/', CustomersListApiView.as_view(), name='customers_list'),
    path('Vaccine/', VaccineListApiView.as_view(), name='Vaccine'),
    path('Vaccine/<str:pk>/', VaccineDetailApiView.as_view(), name='vaccine_detail'),
    path('review/', ReviewCreateView.as_view(), name='reviews'),
    path('made_in/', MadeInListApiView.as_view(), name='made_in'),
    path('voice/', SaveAudioListApiView.as_view(), name = 'voice'),
    path('statistic/', StatisticsListAPiView.as_view(), name = 'statics')

]
