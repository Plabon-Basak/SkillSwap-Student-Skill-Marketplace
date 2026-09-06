"""URL routing for the profiles app."""

from django.urls import path

from apps.profiles import views

urlpatterns = [
    path('profiles/me/', views.MyProfileView.as_view(), name='profile-me'),
    path('profiles/', views.ProfileListView.as_view(), name='profile-list'),
    path(
        'profiles/<str:username>/',
        views.ProfileDetailView.as_view(),
        name='profile-detail',
    ),
    path('skills/', views.SkillListView.as_view(), name='skill-list'),
]
