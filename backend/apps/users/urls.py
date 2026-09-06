"""URL routing for user accounts and authentication."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', views.MeView.as_view(), name='auth-me'),
    path(
        'auth/email/verification/request/',
        views.EmailVerificationRequestView.as_view(),
        name='auth-email-verification-request',
    ),
    path(
        'auth/email/verification/verify/',
        views.EmailVerificationVerifyView.as_view(),
        name='auth-email-verification-verify',
    ),
    path(
        'auth/password-reset/request/',
        views.PasswordResetRequestView.as_view(),
        name='auth-password-reset-request',
    ),
    path(
        'auth/password-reset/verify/',
        views.PasswordResetVerifyView.as_view(),
        name='auth-password-reset-verify',
    ),
]
