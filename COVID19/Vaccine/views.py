from collections import OrderedDict

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from .serializers import CategorySerializer, BaseVaccineSerializer, CustomerSerializer, \
  ReviewCreateSerializers, MadeInSerializers, StatisticsSerializer, VoiceSerializer
from .models import Category, Vaccine, Customer, Review, MadeIn, Voice, Statistics


class VaccinePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('objects_count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('items', data)
        ]))


class MadeInListApiView(ListAPIView):
    serializer_class = MadeInSerializers
    queryset = MadeIn.objects.all()


class CategoryListApiView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class CategoryApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class VaccineListApiView(ListCreateAPIView):
    serializer_class = BaseVaccineSerializer
    pagination_class = VaccinePagination
    queryset = Vaccine.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['price', 'title', 'ip']


class VaccineDetailApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = BaseVaccineSerializer
    queryset = Vaccine.objects.all()


class CustomersListApiView(ListAPIView):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


class ReviewCreateView(ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializers

    def post(self, request):
        review = ReviewCreateSerializers(data=request.data)
        if review.is_valid:
            review.save()


class StatisticsListAPiView(ListAPIView):
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer


class SaveAudioListApiView(ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializers

    def post(self, request):
        audio_file = request.FILES.get('recorded_audio')
        myObj = Voice
        myObj.voice_record = audio_file
        myObj.save()
        return JsonResponse({
            'success': True,
        })
