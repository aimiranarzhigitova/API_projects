"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers

from blog.views import CustomLogoutView, PostImagesViewSet
from blog_api.views import UserRegistrationView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    info=openapi.Info(
        title='Blog Project',
        default_version='v1',
        description='this is test blog project',
        terms_of_service='http://www.google.com/policies/terms/',
        contact=openapi.Contact(email='test@gmail.com'),
        license=openapi.License(name='BSD License')
    ),
    public=True,
    permission_classes=(permissions.AllowAny, ),
)

router = routers.SimpleRouter()
router.register('post_images', PostImagesViewSet)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/', include('blog_api.urls')),
    path('api/v1/users/register/', UserRegistrationView.as_view()),
    path('api/v1/rest-auth/logout/', CustomLogoutView.as_view()),
    path('api/v1/rest-auth/', include('rest_auth.urls')),
]
urlpatterns += static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)
urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
