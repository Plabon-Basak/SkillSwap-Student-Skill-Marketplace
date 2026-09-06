"""URL routing for notifications."""

from django.urls import path

from apps.notifications import views

urlpatterns = [
    path(
        'notifications/mine/',
        views.MyNotificationsView.as_view(),
        name='notification-mine',
    ),
    path(
        'notifications/unread-count/',
        views.NotificationUnreadCountView.as_view(),
        name='notification-unread-count',
    ),
    path(
        'notifications/read-all/',
        views.NotificationReadAllView.as_view(),
        name='notification-read-all',
    ),
    path(
        'notifications/<int:pk>/read/',
        views.NotificationReadView.as_view(),
        name='notification-read',
    ),
]
