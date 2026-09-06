"""URL routing for order conversation threads."""

from django.urls import path

from apps.messaging import views

urlpatterns = [
    path('threads/mine/', views.MyThreadsView.as_view(), name='thread-mine'),
    path(
        'threads/unread-count/',
        views.ThreadUnreadCountView.as_view(),
        name='thread-unread-count',
    ),
    path('threads/<int:pk>/', views.ThreadDetailView.as_view(), name='thread-detail'),
    path(
        'threads/<int:pk>/messages/',
        views.ThreadMessageListCreateView.as_view(),
        name='thread-messages',
    ),
]
