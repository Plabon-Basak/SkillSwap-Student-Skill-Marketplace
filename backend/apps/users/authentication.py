"""JWT authentication that honours user suspension.

SimpleJWT's default authenticator does not check ``is_active``, so a suspended
user's existing tokens would keep working. This subclass rejects tokens for
accounts that have been deactivated (suspended) by moderators.
"""

from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication


class UserJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not user.is_active:
            raise exceptions.AuthenticationFailed('This account has been suspended.')
        return user
