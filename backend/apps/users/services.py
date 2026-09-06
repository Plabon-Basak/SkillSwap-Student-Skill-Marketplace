"""Business logic for authentication flows.

Views and serializers stay thin; security-sensitive operations (OTP
issuance/verification, mail delivery) live here so they can be reused by API
views, Celery tasks (later phases) and the test suite.
"""

import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core import mail
from django.core.mail import EmailMessage
from django.utils import timezone

from apps.users.models import OneTimePassword, OneTimePasswordPurpose, User

OTP_CODE_LENGTH = 6
OTP_MAX_ATTEMPTS = 5


def _otp_validity_seconds() -> int:
    return getattr(settings, 'OTP_CODE_VALIDITY_SECONDS', 600)


def _generate_otp_code() -> str:
    """Generate a cryptographically random 6-digit code, zero-padded."""
    return f'{secrets.randbelow(10**OTP_CODE_LENGTH):0{OTP_CODE_LENGTH}d}'


def _build_email(subject: str, body: str, to: str) -> EmailMessage:
    return EmailMessage(subject=subject, body=body, to=[to])


def send_email(subject: str, body: str, to: str) -> None:
    """Deliver an email through the configured mailer (synchronous for now)."""
    message = _build_email(subject, body, to)
    mail.mailers.default.send_messages([message])


def issue_otp(user: User, purpose: OneTimePasswordPurpose) -> None:
    """Create a fresh OTP for ``user``/``purpose`` and email it to them.

    Any previously outstanding (unused) OTP for the same user/purpose is
    superseded so that only one active code exists at a time.
    """
    OneTimePassword.objects.filter(user=user, purpose=purpose, is_used=False).update(
        is_used=True
    )

    code = _generate_otp_code()
    hashed = make_password(str(code))
    expires_at = timezone.now() + timezone.timedelta(seconds=_otp_validity_seconds())

    OneTimePassword.objects.create(
        user=user,
        purpose=purpose,
        hashed_code=hashed,
        expires_at=expires_at,
    )

    if purpose == OneTimePasswordPurpose.EMAIL_VERIFICATION:
        subject = 'SkillSwap: verify your email address'
        body = (
            f'Your SkillSwap verification code is {code}. '
            f'It expires in {_otp_validity_seconds() // 60} minutes.'
        )
    else:
        subject = 'SkillSwap: reset your password'
        body = (
            f'Your SkillSwap password reset code is {code}. '
            f'It expires in {_otp_validity_seconds() // 60} minutes.'
        )

    send_email(subject, body, user.email)


def verify_otp(user: User, purpose: OneTimePasswordPurpose, code: str) -> bool:
    """Validate and consume an OTP.

    - A wrong code increments the attempt counter.
    - The code is invalid after ``OTP_MAX_ATTEMPTS`` failed attempts, on
      expiry, or once used. Invalid codes are marked used so a brute force
      cannot keep hammering an expired record.
    """
    code = code.strip()
    try:
        otp = OneTimePassword.objects.get(user=user, purpose=purpose, is_used=False)
    except OneTimePassword.DoesNotExist:
        return False

    if timezone.now() > otp.expires_at:
        otp.is_used = True
        otp.save(update_fields=['is_used'])
        return False

    if otp.attempts >= OTP_MAX_ATTEMPTS:
        otp.is_used = True
        otp.save(update_fields=['is_used', 'attempts'])
        return False

    valid = check_password(code, otp.hashed_code)
    if valid:
        otp.is_used = True
        otp.save(update_fields=['is_used'])
    else:
        otp.attempts += 1
        otp.save(update_fields=['attempts'])
    return valid


def ensure_email_verified(user: User) -> None:
    """Mark the user's email as verified for the email-verification purpose."""
    if not user.email_verified:
        user.email_verified = True
        user.save(update_fields=['email_verified'])
