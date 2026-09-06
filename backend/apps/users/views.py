"""Authentication API views.

Views delegate all security-sensitive work to ``apps.users.services`` and use
per-view DRF throttles to blunt credential-stuffing and OTP brute force.
"""

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users import services
from apps.users.models import OneTimePasswordPurpose, User
from apps.users.serializers import (
    LoginSerializer,
    LogoutSerializer,
    OTPCodeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_register'
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        services.issue_otp(user, OneTimePasswordPurpose.EMAIL_VERIFICATION)


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_login'
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = RefreshToken(serializer.validated_data['refresh'])
        token.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class EmailVerificationRequestView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_otp_request'
    serializer_class = OTPCodeSerializer

    def post(self, request, *args, **kwargs):
        if request.user.email_verified:
            return Response(
                {'detail': 'Your email address is already verified.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        services.issue_otp(request.user, OneTimePasswordPurpose.EMAIL_VERIFICATION)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailVerificationVerifyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_otp_verify'
    serializer_class = OTPCodeSerializer

    def post(self, request, *args, **kwargs):
        if request.user.email_verified:
            return Response(
                {'detail': 'Your email address is already verified.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verified = services.verify_otp(
            request.user,
            OneTimePasswordPurpose.EMAIL_VERIFICATION,
            serializer.validated_data['code'],
        )
        if not verified:
            return Response(
                {'code': 'Invalid or expired verification code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        services.ensure_email_verified(request.user)
        return Response({'detail': 'Email address verified.'})


class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_password_reset_request'
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email__iexact=serializer.validated_data['email']
        ).first()
        if user is not None:
            services.issue_otp(user, OneTimePasswordPurpose.PASSWORD_RESET)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetVerifyView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_password_reset_verify'
    serializer_class = PasswordResetVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        verified = services.verify_otp(
            user,
            OneTimePasswordPurpose.PASSWORD_RESET,
            serializer.validated_data['code'],
        )
        if not verified:
            return Response(
                {'code': 'Invalid or expired verification code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        return Response({'detail': 'Password reset successfully.'})
