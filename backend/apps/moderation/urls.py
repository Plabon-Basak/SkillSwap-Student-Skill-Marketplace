"""URL routing for the moderation app."""

from django.urls import path

from apps.moderation import views

urlpatterns = [
    path('reports/', views.ReportListView.as_view(), name='report-list'),
    path('reports/create/', views.ReportCreateView.as_view(), name='report-create'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path(
        'moderation/users/<int:pk>/',
        views.UserModerationView.as_view(),
        name='moderation-user',
    ),
    path(
        'moderation/listings/',
        views.ListingModerationsView.as_view(),
        name='moderation-listing-list',
    ),
    path(
        'moderation/listings/<int:pk>/',
        views.ListingModerationView.as_view(),
        name='moderation-listing-detail',
    ),
]
