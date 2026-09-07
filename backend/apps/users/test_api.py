"""API tests for authentication: registration, login, JWT lifecycle,
email verification, password reset, throttling and suspension handling."""

import re
from unittest import mock

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users import services
from apps.users.models import OneTimePasswordPurpose, User

CODE_RE = re.compile(r'(?:verification|reset) code is (\d{6})')


def extract_code() -> str:
    """Pull the latest OTP out of the test email outbox."""
    return CODE_RE.search(mail.outbox[-1].body).group(1)


class AuthTestBase(TestCase):
    def setUp(self):
        # DRF throttle counters live in the cache and persist between tests;
        # reset so each test begins with a clean slate.
        cache.clear()
        mail.outbox.clear()

    def create_user(self, **kwargs):
        defaults = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'strong-pass-123',
        }
        defaults.update(kwargs)
        return User.objects.create_user(
            username=defaults['username'],
            email=defaults['email'],
            password=defaults['password'],
        )

    def register(self, **overrides):
        payload = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'strong-pass-123',
        }
        payload.update(overrides)
        return self.client.post(
            reverse('auth-register'), payload, content_type='application/json'
        )

    def login(self, identifier='alice@example.com', password='strong-pass-123'):
        return self.client.post(
            reverse('auth-login'),
            {'identifier': identifier, 'password': password},
            content_type='application/json',
        )

    def auth_headers(self, user):
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}


class RegistrationTests(AuthTestBase):
    def test_register_creates_user_and_sends_otp(self):
        response = self.register()

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='alice@example.com')
        self.assertFalse(user.email_verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('alice@example.com', mail.outbox[0].to)
        self.assertIn('verification code', mail.outbox[0].body)

    def test_register_requires_unique_email(self):
        self.register()
        response = self.register(username='alice2')

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())

    def test_register_requires_unique_username(self):
        self.register()
        response = self.register(email='alice2@example.com')

        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.json())

    def test_register_rejects_invalid_email(self):
        response = self.register(email='not-an-email')

        self.assertEqual(response.status_code, 400)

    def test_register_rejects_weak_password(self):
        response = self.register(password='123456')

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.json())

    def test_register_does_not_store_plaintext_password(self):
        self.register()
        user = User.objects.get(email='alice@example.com')

        self.assertNotEqual(user.password, 'strong-pass-123')
        self.assertTrue(user.password.startswith('pbkdf2'))


class LoginTests(AuthTestBase):
    def test_login_with_email(self):
        self.create_user()
        response = self.login()

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['user']['email'], 'alice@example.com')
        self.assertNotIn('password', data)

    def test_login_with_username(self):
        self.create_user()
        response = self.login(identifier='alice')

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())

    def test_login_wrong_password(self):
        self.create_user()
        response = self.login(password='wrong-password')

        self.assertEqual(response.status_code, 400)

    def test_login_unknown_user(self):
        response = self.login(identifier='nobody@example.com')

        self.assertEqual(response.status_code, 400)

    def test_login_inactive_user_rejected(self):
        user = self.create_user()
        user.is_active = False
        user.save(update_fields=['is_active'])
        response = self.login()

        self.assertEqual(response.status_code, 400)


class TokenLifecycleTests(AuthTestBase):
    def test_refresh_rotates_tokens(self):
        self.create_user()
        refresh = str(RefreshToken.for_user(User.objects.get()))

        response = self.client.post(
            reverse('auth-refresh'),
            {'refresh': refresh},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())

    def test_reuse_of_rotated_refresh_token_rejected(self):
        self.create_user()
        user = User.objects.get()
        refresh = str(RefreshToken.for_user(user))

        response = self.client.post(
            reverse('auth-refresh'),
            {'refresh': refresh},
            content_type='application/json',
        )
        old_refresh = response.json()['refresh']
        # One reuse is consumed by the rotation itself; a second is invalid.
        self.client.post(
            reverse('auth-refresh'),
            {'refresh': old_refresh},
            content_type='application/json',
        )
        repeat = self.client.post(
            reverse('auth-refresh'),
            {'refresh': old_refresh},
            content_type='application/json',
        )

        self.assertIn(repeat.status_code, [400, 401])

    def test_refresh_with_invalid_token(self):
        response = self.client.post(
            reverse('auth-refresh'),
            {'refresh': 'not-a-token'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)

    def test_logout_blacklists_refresh_token(self):
        self.create_user()
        refresh = str(RefreshToken.for_user(User.objects.get()))

        logout = self.client.post(
            reverse('auth-logout'),
            {'refresh': refresh},
            content_type='application/json',
            **self.auth_headers(User.objects.get()),
        )
        reuse = self.client.post(
            reverse('auth-refresh'),
            {'refresh': refresh},
            content_type='application/json',
        )

        self.assertEqual(logout.status_code, 204)
        self.assertIn(reuse.status_code, [400, 401])

    def test_logout_requires_authentication(self):
        response = self.client.post(
            reverse('auth-logout'), {'refresh': 'x'}, content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)


class MeEndpointTests(AuthTestBase):
    def test_me_requires_authentication(self):
        response = self.client.get(reverse('auth-me'))

        self.assertEqual(response.status_code, 401)

    def test_me_returns_current_user(self):
        user = self.create_user()
        response = self.client.get(reverse('auth-me'), **self.auth_headers(user))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], 'alice@example.com')

    def test_suspended_user_token_is_rejected(self):
        user = self.create_user()
        user.is_active = False
        user.save(update_fields=['is_active'])

        response = self.client.get(reverse('auth-me'), **self.auth_headers(user))

        self.assertEqual(response.status_code, 401)


class EmailVerificationTests(AuthTestBase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.headers = self.auth_headers(self.user)
        self.user.refresh_from_db()

    def request_otp(self):
        return self.client.post(
            reverse('auth-email-verification-request'), **self.headers
        )

    def verify(self, code):
        return self.client.post(
            reverse('auth-email-verification-verify'),
            {'code': code},
            content_type='application/json',
            **self.headers,
        )

    def test_request_otp_sends_email(self):
        response = self.request_otp()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)

    def test_verify_email_with_correct_code(self):
        self.request_otp()
        response = self.verify(extract_code())

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_verify_email_with_wrong_code(self):
        self.request_otp()
        response = self.verify('000000')

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_verified)

    def test_verify_email_requires_authentication(self):
        response = self.client.post(
            reverse('auth-email-verification-verify'),
            {'code': '000000'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)

    def test_second_otp_supersedes_first(self):
        self.request_otp()
        first_code = extract_code()
        self.request_otp()

        first_response = self.verify(first_code)
        second_response = self.verify(extract_code())

        self.assertEqual(first_response.status_code, 400)
        self.assertEqual(second_response.status_code, 200)

    def test_cannot_request_otp_when_already_verified(self):
        self.request_otp()
        self.verify(extract_code())

        response = self.request_otp()
        self.assertEqual(response.status_code, 400)

    def test_allows_only_one_active_otp(self):
        self.request_otp()
        self.request_otp()

        active = self.user.one_time_passwords.filter(is_used=False)
        self.assertEqual(active.count(), 1)


class PasswordResetTests(AuthTestBase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user()

    def request_reset(self, email='alice@example.com'):
        return self.client.post(
            reverse('auth-password-reset-request'),
            {'email': email},
            content_type='application/json',
        )

    def reset_password(
        self, code, email='alice@example.com', new_password='new-strong-pass-456'
    ):
        return self.client.post(
            reverse('auth-password-reset-verify'),
            {'email': email, 'code': code, 'new_password': new_password},
            content_type='application/json',
        )

    def test_request_reset_sends_otp(self):
        response = self.request_reset()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('password reset code', mail.outbox[0].body.lower())

    def test_request_reset_for_unknown_email_is_uniform(self):
        response = self.request_reset(email='ghost@example.com')

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_password_with_correct_code(self):
        self.request_reset()
        code = extract_code()

        response = self.reset_password(code)

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new-strong-pass-456'))
        self.assertFalse(self.user.check_password('strong-pass-123'))

    def test_reset_password_with_wrong_code(self):
        self.request_reset()

        response = self.reset_password('000000')

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('strong-pass-123'))

    def test_otp_is_single_use(self):
        self.request_reset()
        code = extract_code()

        self.reset_password(code)
        repeat = self.reset_password(code, new_password='another-pass-789')

        self.assertEqual(repeat.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new-strong-pass-456'))

    def test_reset_rejects_weak_new_password(self):
        self.request_reset()
        code = extract_code()

        response = self.reset_password(code, new_password='weak')

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('strong-pass-123'))


class BruteForceThrottleTests(AuthTestBase):
    def test_login_is_rate_limited(self):
        self.create_user()

        # SimpleRateThrottle.THROTTLE_RATES is captured at import time, so a
        # settings override would not be picked up; patch the class attribute.
        with mock.patch.object(
            ScopedRateThrottle, 'THROTTLE_RATES', {'auth_login': '2/min'}
        ):
            self.login()
            wrong_creds = self.login('ghost@example.com')
            self.assertEqual(wrong_creds.status_code, 400)
            limited = self.login('ghost@example.com')
            self.assertEqual(limited.status_code, 429)


class OTPModelTests(AuthTestBase):
    def test_otp_code_is_stored_hashed(self):
        user = self.create_user()

        services.issue_otp(user, OneTimePasswordPurpose.EMAIL_VERIFICATION)

        otp = user.one_time_passwords.get()
        self.assertNotEqual(otp.hashed_code, extract_code())
        self.assertTrue(otp.hashed_code.startswith('pbkdf2'))

    def test_expired_otp_is_rejected_and_marked_used(self):
        from django.utils import timezone

        user = self.create_user()
        services.issue_otp(user, OneTimePasswordPurpose.EMAIL_VERIFICATION)
        otp = user.one_time_passwords.get()
        otp.expires_at = timezone.now() - timezone.timedelta(minutes=1)
        otp.save(update_fields=['expires_at'])

        ok = services.verify_otp(
            user, OneTimePasswordPurpose.EMAIL_VERIFICATION, extract_code()
        )

        self.assertFalse(ok)
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)

    def test_otp_rejected_after_max_attempts(self):
        user = self.create_user()
        services.issue_otp(user, OneTimePasswordPurpose.EMAIL_VERIFICATION)
        code = extract_code()
        wrong = '999999' if code != '999999' else '888888'

        for _ in range(5):
            self.assertFalse(
                services.verify_otp(
                    user, OneTimePasswordPurpose.EMAIL_VERIFICATION, wrong
                )
            )

        # Even the correct code is rejected once attempts are exhausted.
        self.assertFalse(
            services.verify_otp(user, OneTimePasswordPurpose.EMAIL_VERIFICATION, code)
        )
        otp = user.one_time_passwords.get()
        self.assertTrue(otp.is_used)
