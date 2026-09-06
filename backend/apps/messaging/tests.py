"""Tests for order conversation threads and messages."""

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.listings.models import Category
from apps.listings.services import accept_application, apply_to_listing
from apps.messaging.models import Message, Thread
from apps.messaging.services import unread_count_for
from apps.notifications.models import Notification
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


def setup_order_with_thread():
    """Create an accepted application + order; returns dict of actors."""
    provider = make_player('provider')
    make_profile(provider, bio='pro provider')
    buyer = make_player('buyer')
    buyer_profile = make_profile(buyer)
    listing = make_listing(provider)
    application = apply_to_listing(listing, buyer_profile)
    accept_application(application)
    order_response = client().post(
        reverse('order-list'),
        {'application': application.id},
        format='json',
        **auth(buyer),
    )
    assert order_response.status_code == 201, order_response.content
    return {
        'provider': provider,
        'provider_profile': provider.profile,
        'buyer': buyer,
        'buyer_profile': buyer_profile,
        'listing': listing,
        'application': application,
        'order': application.order,
        'thread': application.order.thread,
    }


class ThreadSetupMixin(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.data = setup_order_with_thread()
        self.provider = self.data['provider']
        self.buyer = self.data['buyer']
        self.thread = self.data['thread']


class ThreadTests(ThreadSetupMixin):
    def test_thread_created_with_order(self):
        thread = Thread.objects.get(order=self.data['order'])
        self.assertEqual(thread.buyer, self.data['buyer_profile'])
        self.assertEqual(thread.provider, self.data['provider_profile'])

    def test_participants_list_their_threads(self):
        for user in (self.buyer, self.provider):
            response = client().get(reverse('thread-mine'), **auth(user))
            self.assertEqual(response.status_code, 200)
            ids = [t['id'] for t in response.json()['results']]
            self.assertIn(self.thread.id, ids)

    def test_stranger_gets_404(self):
        stranger = make_player('stranger')
        make_profile(stranger)
        response = client().get(
            reverse('thread-detail', args=[self.thread.id]), **auth(stranger)
        )
        self.assertEqual(response.status_code, 404)

    def test_requires_auth(self):
        response = client().get(reverse('thread-mine'))
        self.assertEqual(response.status_code, 401)

    def test_requires_verified_email(self):
        unverified = make_player('unverified', verified=False)
        make_profile(unverified)
        response = client().get(reverse('thread-mine'), **auth(unverified))
        self.assertEqual(response.status_code, 403)

    def test_thread_detail_serializes_order_and_participants(self):
        response = client().get(
            reverse('thread-detail', args=[self.thread.id]), **auth(self.buyer)
        )
        payload = response.json()
        self.assertEqual(payload['order'], self.data['order'].id)
        self.assertEqual(payload['buyer']['username'], self.buyer.username)
        self.assertEqual(payload['provider']['username'], self.provider.username)


class MessageTests(ThreadSetupMixin):
    def _send(self, user, body='Hello!', thread=None):
        thread = thread or self.thread
        return client().post(
            reverse('thread-messages', args=[thread.id]),
            {'body': body},
            format='json',
            **auth(user),
        )

    def test_send_and_read_message(self):
        response = self._send(self.buyer, 'Is Monday ok?')
        self.assertEqual(response.status_code, 201)
        message = Message.objects.get(thread=self.thread)
        self.assertEqual(message.body, 'Is Monday ok?')
        self.assertEqual(message.sender, self.data['buyer_profile'])

        listing = client().get(
            reverse('thread-messages', args=[self.thread.id]), **auth(self.provider)
        )
        self.assertEqual(listing.status_code, 200)
        bodies = [m['body'] for m in listing.json()['results']]
        self.assertIn('Is Monday ok?', bodies)

    def test_stranger_cannot_message(self):
        stranger = make_player('stranger2')
        make_profile(stranger)
        response = self._send(stranger)
        self.assertEqual(response.status_code, 404)

    def test_blank_message_rejected(self):
        response = self._send(self.buyer, '   ')
        self.assertEqual(response.status_code, 400)

    def test_staff_cannot_post(self):
        staff = make_player('admin', is_staff=True)
        response = self._send(staff, 'Admin note')
        self.assertEqual(response.status_code, 403)

    def test_message_notifies_participant(self):
        self._send(self.buyer, 'Hello provider')
        notification = Notification.objects.filter(
            recipient=self.provider, verb='new_message'
        )
        self.assertEqual(notification.count(), 1)
        self.assertEqual(notification.first().data['order_id'], self.data['order'].id)

    def test_unread_counts_only_for_recipient(self):
        self._send(self.buyer, 'first')
        self._send(self.buyer, 'second')
        self.assertEqual(
            unread_count_for(self.thread, self.data['provider_profile']), 2
        )
        self.assertEqual(unread_count_for(self.thread, self.data['buyer_profile']), 0)

    def test_thread_unread_count_endpoint(self):
        self._send(self.buyer, 'hungry for help')
        response = client().get(reverse('thread-unread-count'), **auth(self.provider))
        self.assertEqual(response.json()['count'], 1)

    def test_getting_thread_marks_inbound_read(self):
        self._send(self.buyer, 'marked please')
        unread_before = (
            client()
            .get(reverse('thread-unread-count'), **auth(self.provider))
            .json()['count']
        )
        self.assertEqual(unread_before, 1)
        client().get(
            reverse('thread-detail', args=[self.thread.id]), **auth(self.provider)
        )
        unread_after = (
            client()
            .get(reverse('thread-unread-count'), **auth(self.provider))
            .json()['count']
        )
        self.assertEqual(unread_after, 0)

    def test_messages_ordered_by_creation(self):
        self._send(self.buyer, 'one')
        self._send(self.buyer, 'two')
        listing = (
            client()
            .get(
                reverse('thread-messages', args=[self.thread.id]), **auth(self.provider)
            )
            .json()['results']
        )
        self.assertEqual([m['body'] for m in listing], ['one', 'two'])
