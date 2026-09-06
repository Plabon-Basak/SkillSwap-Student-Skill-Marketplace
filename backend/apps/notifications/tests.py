"""Tests for the notification center and event-driven notifications."""

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.listings.models import Category
from apps.listings.services import (
    accept_application,
    apply_to_listing,
    reject_application,
)
from apps.messaging.services import send_message
from apps.notifications.models import Notification
from apps.notifications.services import unread_count_for
from apps.profiles.models import Profile


def make_player(username='alice', verified=True, **kwargs):
    from apps.users.models import User

    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='strong-pass-123',
        **kwargs,
    )
    if verified:
        user.email_verified = True
        user.save(update_fields=['email_verified'])
    return user


def make_profile(user, **kwargs):
    profile_kwargs = {'university': 'Example U', 'bio': 'tutor'}
    profile_kwargs.update(kwargs)
    return Profile.objects.create(user=user, **profile_kwargs)


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}


def client():
    from django.test import Client as DjangoClient

    return DjangoClient()


def make_category(name='Tutoring'):
    category, _ = Category.objects.get_or_create(name=name)
    return category


def make_listing(provider_user):
    response = client().post(
        reverse('listing-list'),
        {
            'title': f'{provider_user.username} math help',
            'description': 'Weekly 1:1 sessions.',
            'price': '50.00',
            'category': make_category().slug,
            'skills': ['Mathematics'],
            'delivery_time_days': 7,
            'is_remote': True,
        },
        format='json',
        **auth(provider_user),
    )
    assert response.status_code == 201, response.content
    from apps.listings.models import Listing

    return Listing.objects.get(slug=response.json()['slug'])


class ScenarioSetupMixin(TestCase):
    """Provider + buyer with a pending application ready to resolve."""

    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.provider = make_player('provider')
        self.provider_profile = make_profile(self.provider, bio='pro provider')
        self.buyer = make_player('buyer')
        self.buyer_profile = make_profile(self.buyer)
        self.listing = make_listing(self.provider)
        self.application = apply_to_listing(
            self.listing, self.buyer_profile, message='Please accept me.'
        )

    def _create_order(self):
        accept_application(self.application)
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            format='json',
            **auth(self.buyer),
        )
        assert response.status_code == 201, response.content
        return self.application.order


class EventNotificationTests(ScenarioSetupMixin):
    def test_accept_notifies_applicant(self):
        accept_application(self.application)
        n = Notification.objects.get(recipient=self.buyer, verb='application_accepted')
        self.assertEqual(n.data['listing_id'], self.listing.id)

    def test_reject_notifies_applicant(self):
        reject_application(self.application)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.buyer, verb='application_rejected'
            ).exists()
        )

    def test_order_creation_notifies_provider(self):
        order = self._create_order()
        n = Notification.objects.get(recipient=self.provider, verb='new_order')
        self.assertEqual(n.target_id, order.id)

    def test_payment_notifies_provider(self):
        order = self._create_order()
        client().post(
            reverse('order-mock-confirm', args=[order.id]), **auth(self.buyer)
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.provider, verb='order_paid', target_id=order.id
            ).exists()
        )

    def test_start_and_complete_notify_buyer(self):
        order = self._create_order()
        client().post(
            reverse('order-mock-confirm', args=[order.id]), **auth(self.buyer)
        )
        client().patch(
            reverse('order-detail', args=[order.id]),
            {'action': 'start'},
            content_type='application/json',
            **auth(self.provider),
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.buyer, verb='order_started', target_id=order.id
            ).exists()
        )
        client().patch(
            reverse('order-detail', args=[order.id]),
            {'action': 'complete'},
            content_type='application/json',
            **auth(self.provider),
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.buyer, verb='order_completed', target_id=order.id
            ).exists()
        )

    def test_cancel_notifies_counterparty(self):
        self.application.proposed_price = '40.00'
        self.application.save(update_fields=['proposed_price'])
        order = self._create_order()
        client().patch(
            reverse('order-detail', args=[order.id]),
            {'action': 'cancel'},
            content_type='application/json',
            **auth(self.provider),
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.buyer,
                verb='order_cancelled',
                target_id=order.id,
                actor=self.provider,
            ).exists()
        )

    def test_message_notifies_other_participant(self):
        order = self._create_order()
        send_message(order.thread, self.buyer_profile, body='Hi provider')
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.provider, verb='new_message'
            ).exists()
        )


class NotificationCenterTests(ScenarioSetupMixin):
    def setUp(self):
        super().setUp()
        self.order = self._create_order()
        client().post(
            reverse('order-mock-confirm', args=[self.order.id]), **auth(self.buyer)
        )

    def test_read_single_notification(self):
        unread = Notification.objects.get(recipient=self.provider, verb='order_paid')
        response = client().post(
            reverse('notification-read', args=[unread.id]), **auth(self.provider)
        )
        self.assertEqual(response.status_code, 200)
        unread.refresh_from_db()
        self.assertTrue(unread.is_read)

    def test_read_single_foreign_notification_404(self):
        other = Notification.objects.get(recipient=self.provider, verb='order_paid')
        response = client().post(
            reverse('notification-read', args=[other.id]), **auth(self.buyer)
        )
        self.assertEqual(response.status_code, 404)

    def test_unread_filter_and_count(self):
        listing = (
            client()
            .get(
                reverse('notification-mine'),
                {'unread': 'true'},
                **auth(self.provider),
            )
            .json()
        )

        count_endpoint = (
            client()
            .get(reverse('notification-unread-count'), **auth(self.provider))
            .json()
        )
        expected_unread = unread_count_for(self.provider)
        self.assertEqual(len(listing['results']), expected_unread)
        self.assertTrue(all(not n['is_read'] for n in listing['results']))
        self.assertEqual(count_endpoint['count'], expected_unread)

    def test_requires_auth(self):
        self.assertEqual(client().get(reverse('notification-mine')).status_code, 401)
        self.assertEqual(
            client().get(reverse('notification-unread-count')).status_code, 401
        )

    def test_requires_verified_email(self):
        unverified = make_player('unverified', verified=False)
        make_profile(unverified)
        response = client().get(reverse('notification-mine'), **auth(unverified))
        self.assertEqual(response.status_code, 403)

    def test_recipient_only_endpoint(self):
        other = Notification.objects.get(recipient=self.provider, verb='order_paid')
        response = client().get(reverse('notification-mine'), **auth(self.buyer))
        ids = [n['id'] for n in response.json()['results']]
        self.assertNotIn(other.id, ids)

    def test_read_all(self):
        expected_unread = unread_count_for(self.provider)
        response = client().post(
            reverse('notification-read-all'), **auth(self.provider)
        )
        self.assertEqual(response.json()['marked_read'], expected_unread)
        self.assertEqual(unread_count_for(self.provider), 0)
