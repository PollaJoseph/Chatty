from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, re_path, include

schema_view = get_schema_view(
    openapi.Info(
        title="Qasr El Kbabgi",
        default_version='v1',
        description="Qasr El Kbabgi URLs, APIs documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Django admin interface for managing the database models in the admin panel.
    path('admin/', admin.site.urls),

    # APIs from local apps
    path('userdata/', include('userdata.urls')),

    # API documentation using Swagger/OpenAPI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc'), name='schema-redoc'),
]