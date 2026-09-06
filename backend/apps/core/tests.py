"""Tests for core infrastructure endpoints."""

from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_health_check_returns_ok(self):
        response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertEqual(response.json()['database'], 'ok')

    def test_health_check_is_public(self):
        response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, 200)
