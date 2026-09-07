"""Root URL configuration for the SkillSwap project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # API documentation (OpenAPI schema, Swagger UI, ReDoc).
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/v1/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-schema-swagger-ui',
    ),
    path(
        'api/v1/schema/redoc/',
        SpectacularRedocView.as_view(url_name='api-schema'),
        name='api-schema-redoc',
    ),
    # Versioned API namespace. Each app contributes its own routes.
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.profiles.urls')),
    path('api/v1/', include('apps.listings.urls')),
    path('api/v1/', include('apps.orders.urls')),
    path('api/v1/', include('apps.messaging.urls')),
    path('api/v1/', include('apps.notifications.urls')),
    path('api/v1/', include('apps.reviews.urls')),
    path('api/v1/', include('apps.moderation.urls')),
]

# Serve uploaded media during development only; production uses a real
# static/media host or object storage.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
