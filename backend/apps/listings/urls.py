"""URL routing for the marketplace listings app."""

from django.urls import path

from apps.listings import views

urlpatterns = [
    path('listings/', views.ListingListCreateView.as_view(), name='listing-list'),
    path('listings/mine/', views.MyListingsView.as_view(), name='listing-mine'),
    path(
        'listings/<slug:slug>/applications/',
        views.ListingApplicationsView.as_view(),
        name='listing-applications',
    ),
    path(
        'listings/<slug:slug>/',
        views.ListingDetailView.as_view(),
        name='listing-detail',
    ),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path(
        'applications/mine/',
        views.MyApplicationsView.as_view(),
        name='application-mine',
    ),
    path(
        'applications/<int:pk>/',
        views.ApplicationDetailView.as_view(),
        name='application-detail',
    ),
]
