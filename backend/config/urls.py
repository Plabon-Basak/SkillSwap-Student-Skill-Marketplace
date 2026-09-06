"""Root URL configuration for the SkillSwap project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Versioned API namespace. Each app contributes its own routes.
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/', include('apps.users.urls')),
]
