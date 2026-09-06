from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A student on the SkillSwap marketplace.

    A single user model acts as both buyer and seller; role behavior is
    derived from related profiles and listings rather than hard-coded roles.
    """

    email = models.EmailField(unique=True)

    email_verified = models.BooleanField(
        default=False,
        help_text='Designates whether the user verified ownership of their email address.',
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username

    @property
    def is_email_verified(self) -> bool:
        return self.email_verified


class OneTimePasswordPurpose(models.TextChoices):
    EMAIL_VERIFICATION = 'email_verification', 'Email verification'
    PASSWORD_RESET = 'password_reset', 'Password reset'


class OneTimePassword(models.Model):
    """A short-lived, single-use numeric code delivered out-of-band.

    Only the salted password hash of the code is stored so that a database
    leak cannot be used to generate valid codes. Verification uses a
    constant-time comparison through Django's password hashing helpers.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='one_time_passwords'
    )
    purpose = models.CharField(max_length=32, choices=OneTimePasswordPurpose.choices)
    hashed_code = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'purpose', 'is_used'],
                condition=models.Q(is_used=False),
                name='unique_active_otp_per_purpose',
            )
        ]
        indexes = [
            models.Index(fields=['user', 'purpose', 'is_used']),
        ]

    def __str__(self):
        return f'{self.user} {self.purpose} otp'
