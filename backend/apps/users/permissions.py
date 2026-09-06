"""Custom permission classes for the SkillSwap API."""

from rest_framework.permissions import BasePermission


class IsEmailVerified(BasePermission):
    """Allow only authenticated users whose email address is verified."""

    message = 'A verified email address is required.'

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user and user.is_authenticated and getattr(user, 'email_verified', False)
        )
