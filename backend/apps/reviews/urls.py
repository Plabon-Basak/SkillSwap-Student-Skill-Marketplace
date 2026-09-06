"""URL routing for reviews."""

from django.urls import path

from apps.reviews import views

urlpatterns = [
    path('reviews/', views.ReviewCreateView.as_view(), name='review-create'),
    path(
        'profiles/<str:username>/reviews/',
        views.ProfileReviewsView.as_view(),
        name='profile-reviews',
    ),
]
