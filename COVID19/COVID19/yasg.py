from django.urls import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

swagger_info = openapi.Info(
    title="Vaccine API",
    default_version='v1',
    description="""Streisand API Swagger Definition""",  # noqa
    terms_of_service="https://www.something.com/policies/terms/",
    contact=openapi.Contact(email="contact@something.xyz"),
    license=openapi.License(name="MIT License"),
)

SchemaView = get_schema_view(
    validators=['ssv', 'flex'],
    public=True,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    path(r'^swagger(?P<format>.json|.yaml)$', SchemaView.without_ui(cache_timeout=0), name='schema-json'),
    path(r'^swagger/$', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'^redoc/$', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path(r'^cached/swagger(?P<format>.json|.yaml)$', SchemaView.without_ui(cache_timeout=None), name='cschema-json'),
    path(r'^cached/swagger/$', SchemaView.with_ui('swagger', cache_timeout=None), name='cschema-swagger-ui'),
    path(r'^cached/redoc/$', SchemaView.with_ui('redoc', cache_timeout=None), name='cschema-redoc'),
]
