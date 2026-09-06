"""Root URL configuration for the SkillSwap project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Versioned API namespace. Each app contributes its own routes.
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.profiles.urls')),
    path('api/v1/', include('apps.listings.urls')),
]

# Serve uploaded media during development only; production uses a real
# static/media host or object storage.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
