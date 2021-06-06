from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('API.urls')),
    path('admin/', admin.site.urls),
    path('', include('user.urls')),
]
