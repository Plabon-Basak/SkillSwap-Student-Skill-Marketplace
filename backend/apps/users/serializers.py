"""API request/response serializers for authentication flows."""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Public representation of a user (no credentials or secret fields)."""

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'email_verified',
            'date_joined',
        ]
        read_only_fields = ['id', 'email_verified', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Login with either email or username, returning tokens and user data.

    Emits a single field error for unknown credentials so attackers cannot
    distinguish between a valid username and a valid password.
    """

    identifier = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs: dict) -> dict:
        identifier = attrs['identifier']
        password = attrs['password']

        def _login_candidate(candidate: User) -> User | None:
            if candidate is None:
                return None
            return authenticate(
                request=self.context.get('request'),
                username=candidate.username,
                password=password,
            )

        user = _login_candidate(
            User.objects.filter(email__iexact=identifier).first()
        ) or _login_candidate(User.objects.filter(username=identifier).first())

        if user is None or not user.is_active:
            raise serializers.ValidationError(
                'Unable to log in with the provided credentials.'
            )

        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value: str) -> str:
        try:
            RefreshToken(value)
        except Exception as exc:  # noqa: BLE001 — simplejwt raises varied errors
            raise serializers.ValidationError('Invalid refresh token.') from exc
        return value


class OTPCodeSerializer(serializers.Serializer):
    code = serializers.CharField(
        min_length=6,
        max_length=6,
        trim_whitespace=False,
        error_messages={
            'min_length': 'The verification code is 6 digits long.',
            'max_length': 'The verification code is 6 digits long.',
        },
    )


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        # Normalize so lookups and matching are case-insensitive. The response
        # is uniform whether or not the account exists (no enumeration).
        return value.strip().lower()


class PasswordResetVerifySerializer(OTPCodeSerializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_new_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate(self, attrs: dict) -> dict:
        user = User.objects.filter(email__iexact=attrs['email']).first()
        if user is None:
            raise serializers.ValidationError({'email': 'Unknown email address.'})
        attrs['user'] = user
        return attrs
