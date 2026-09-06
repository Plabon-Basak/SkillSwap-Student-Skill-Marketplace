"""URL routing for the core app."""

from django.urls import path

from apps.core import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
]
