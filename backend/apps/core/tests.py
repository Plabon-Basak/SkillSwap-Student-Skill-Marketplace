"""Tests for core infrastructure endpoints."""

from unittest import mock

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import OperationalError
from django.test import TestCase
from django.urls import reverse

from apps.core.validators import MAX_UPLOAD_SIZE, validate_uploaded_image


class HealthCheckTests(TestCase):
    def test_health_check_returns_ok(self):
        response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertEqual(response.json()['database'], 'ok')

    def test_health_check_is_public(self):
        response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, 200)

    def test_health_check_reports_degraded_when_db_unavailable(self):
        with mock.patch(
            'django.db.connection.ensure_connection',
            side_effect=OperationalError('db down'),
        ):
            response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['status'], 'degraded')
        self.assertEqual(response.json()['database'], 'unavailable')


def image(name='photo.png', bytes=b'\x89PNG\r\n\x1a\n', content_type='image/png'):
    return SimpleUploadedFile(name, bytes, content_type=content_type)


class UploadedImageValidatorTests(TestCase):
    def test_valid_image_passes(self):
        validate_uploaded_image(image())

    def test_oversized_image_rejected(self):
        with self.assertRaisesMessage(ValidationError, 'smaller than 5 MB'):
            validate_uploaded_image(image(bytes=b'x' * (MAX_UPLOAD_SIZE + 1)))

    def test_disallowed_content_type_rejected(self):
        with self.assertRaisesMessage(ValidationError, 'JPEG, PNG, WEBP or GIF'):
            validate_uploaded_image(image(content_type='application/pdf'))

    def test_disallowed_extension_rejected(self):
        with self.assertRaisesMessage(ValidationError, 'Unsupported image extension'):
            validate_uploaded_image(image(name='photo.exe'))
