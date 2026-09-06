"""Tests for the custom user model and basic authorization primitives."""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='strong-pass-123',
        )

        self.assertEqual(user.username, 'alice')
        self.assertEqual(user.email, 'alice@example.com')
        self.assertTrue(user.check_password('strong-pass-123'))
        self.assertFalse(user.has_usable_password() is False)

    def test_user_email_is_unique(self):
        User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='strong-pass-123',
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='alice2',
                email='alice@example.com',
                password='strong-pass-123',
            )

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin-pass-123',
        )

        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_user_str(self):
        user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='strong-pass-123',
        )

        self.assertEqual(str(user), 'alice')
