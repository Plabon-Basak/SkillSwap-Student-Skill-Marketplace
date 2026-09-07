"""Tests for orders and payments (lifecycle, checkout, webhook)."""

from unittest import mock

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.listings.models import Category, Listing
from apps.listings.services import accept_application, apply_to_listing
from apps.orders import services
from apps.orders.models import Order, Payment
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


def make_listing(provider_user, **overrides):
    payload = {
        'title': f'{provider_user.username} math help',
        'description': 'Weekly 1:1 sessions.',
        'price': overrides.pop('price', '50.00'),
        'currency': overrides.pop('currency', 'USD'),
        'category': make_category().slug,
        'skills': ['Mathematics'],
        'delivery_time_days': 7,
        'is_remote': True,
    }
    payload.update(overrides)
    response = client().post(
        reverse('listing-list'),
        payload,
        content_type='application/json',
        **auth(provider_user),
    )
    assert response.status_code == 201, response.content
    listing = Listing.objects.get(slug=response.json()['slug'])
    return listing


def accepted_application(provider_user, buyer_user, *, proposed_price=None):
    listing = make_listing(provider_user)
    application = apply_to_listing(
        listing,
        Profile.objects.get(user=buyer_user),
        message='I would like to book this.',
        proposed_price=proposed_price,
    )
    accept_application(application)
    return application


class OrderSetupMixin(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.provider = make_player('provider')
        self.provider_profile = make_profile(self.provider, bio='pro provider')
        self.buyer = make_player('buyer')
        self.buyer_profile = make_profile(self.buyer)
        self.application = accepted_application(self.provider, self.buyer)


class OrderCreationTests(OrderSetupMixin):
    def test_requires_authentication(self):
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_requires_verified_email(self):
        hacker = make_player('hacker', verified=False)
        make_profile(hacker)
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(hacker),
        )
        self.assertEqual(response.status_code, 403)

    def test_create_requires_profile(self):
        no_profile = make_player('noprofile')
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(no_profile),
        )
        self.assertEqual(response.status_code, 400)

    def test_only_applicant_can_order(self):
        stranger = make_player('stranger')
        make_profile(stranger)
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(stranger),
        )
        self.assertEqual(response.status_code, 403)

    def test_create_order_success(self):
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(application=self.application)
        self.assertEqual(order.status, Order.Status.PENDING_PAYMENT)
        self.assertEqual(
            order.price,
            self.application.proposed_price or self.application.listing.price,
        )
        self.assertEqual(order.buyer, self.buyer_profile)
        self.assertEqual(order.provider, self.provider_profile)
        self.assertEqual(Payment.objects.filter(order=order).count(), 1)

    def test_uses_proposed_price_as_agreed_price(self):
        self.application.proposed_price = '40.00'
        self.application.save(update_fields=['proposed_price'])
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id, 'note': 'I bid 40.'},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(application=self.application)
        self.assertEqual(order.price, 40.00)
        self.assertEqual(order.note, 'I bid 40.')

    def test_duplicate_order_rejected(self):
        client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 400)

    def test_pending_application_not_ordered(self):
        listing = make_listing(self.provider)
        pending = apply_to_listing(listing, self.buyer_profile)
        response = client().post(
            reverse('order-list'),
            {'application': pending.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 400)


class OrderLifecycleTests(OrderSetupMixin):
    def _create_order(self):
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 201)
        return response.json()['id']

    def test_full_flow(self):
        order_id = self._create_order()
        checkout = client().post(
            reverse('order-checkout', args=[order_id]), **auth(self.buyer)
        )
        self.assertEqual(checkout.status_code, 200)
        self.assertEqual(checkout.json()['mode'], 'simulation')

        confirm = client().post(
            reverse('order-mock-confirm', args=[order_id]), **auth(self.buyer)
        )
        self.assertEqual(confirm.status_code, 200)
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertIsNotNone(order.paid_at)
        self.assertEqual(order.payment.status, Payment.Status.PAID)

        start = client().patch(
            reverse('order-detail', args=[order_id]),
            {'action': 'start'},
            content_type='application/json',
            **auth(self.provider),
        )
        self.assertEqual(start.status_code, 200)
        self.assertEqual(start.json()['status'], Order.Status.IN_PROGRESS)

        done = client().patch(
            reverse('order-detail', args=[order_id]),
            {'action': 'complete'},
            content_type='application/json',
            **auth(self.provider),
        )
        self.assertEqual(done.status_code, 200)
        self.assertEqual(done.json()['status'], Order.Status.COMPLETED)
        self.assertIsNotNone(Order.objects.get(id=order_id).completed_at)

    def test_cancel_pending_order_by_buyer(self):
        order_id = self._create_order()
        response = client().patch(
            reverse('order-detail', args=[order_id]),
            {'action': 'cancel'},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertIsNotNone(order.cancelled_at)

    def test_cancel_paid_order_rejected(self):
        order_id = self._create_order()
        client().post(
            reverse('order-mock-confirm', args=[order_id]), **auth(self.buyer)
        )
        response = client().patch(
            reverse('order-detail', args=[order_id]),
            {'action': 'cancel'},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 400)

    def test_buyer_cannot_start(self):
        order_id = self._create_order()
        client().post(
            reverse('order-mock-confirm', args=[order_id]), **auth(self.buyer)
        )
        response = client().patch(
            reverse('order-detail', args=[order_id]),
            {'action': 'start'},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 403)

    def test_stranger_cannot_view_or_act(self):
        order_id = self._create_order()
        stranger = make_player('stranger2')
        make_profile(stranger)
        view = client().get(reverse('order-detail', args=[order_id]), **auth(stranger))
        self.assertEqual(view.status_code, 404)
        action = client().patch(
            reverse('order-detail', args=[order_id]),
            {'action': 'cancel'},
            content_type='application/json',
            **auth(stranger),
        )
        self.assertEqual(action.status_code, 404)

    def test_invalid_action_rejected(self):
        order_id = self._create_order()
        response = client().patch(
            reverse('order-detail', args=[order_id]),
            {'action': 'explode'},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 400)

    def test_only_buyer_can_checkout(self):
        order_id = self._create_order()
        response = client().post(
            reverse('order-checkout', args=[order_id]), **auth(self.provider)
        )
        self.assertEqual(response.status_code, 403)


class OrderViewTests(OrderSetupMixin):
    def _create_order(self):
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 201)
        return response.json()['id']

    def test_buyer_and_provider_see_listed_orders(self):
        order_id = self._create_order()
        buyer_view = client().get(reverse('order-list'), **auth(self.buyer))
        self.assertEqual(buyer_view.status_code, 200)
        self.assertIn(order_id, [o['id'] for o in buyer_view.json()['results']])
        provider_view = client().get(reverse('order-list'), **auth(self.provider))
        self.assertIn(order_id, [o['id'] for o in provider_view.json()['results']])

    def test_role_filter(self):
        order_id = self._create_order()
        provider_only = client().get(
            reverse('order-list'), {'role': 'provider'}, **auth(self.buyer)
        )
        self.assertNotIn(order_id, [o['id'] for o in provider_only.json()['results']])

    def test_order_serialization_includes_listing(self):
        order_id = self._create_order()
        detail = client().get(
            reverse('order-detail', args=[order_id]), **auth(self.buyer)
        )
        payload = detail.json()
        self.assertEqual(payload['application'], self.application.id)
        self.assertIn('title', payload['listing'])
        self.assertEqual(payload['buyer']['username'], self.buyer.username)
        self.assertEqual(payload['provider']['username'], self.provider.username)

    def test_guest_cannot_list_orders(self):
        response = client().get(reverse('order-list'))
        self.assertEqual(response.status_code, 401)

    def test_mock_confirm_requires_authentication(self):
        order_id = self._create_order()
        response = client().post(reverse('order-mock-confirm', args=[order_id]))
        self.assertEqual(response.status_code, 401)

    def test_webhook_allowed_without_auth(self):
        response = client().post(
            reverse('stripe-webhook'),
            {'type': 'checkout.session.completed'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)


class RefundServiceTests(OrderSetupMixin):
    def _create_order(self):
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 201)
        return Order.objects.get(application=self.application)

    def test_refund_rejects_unpaid_order(self):
        order = self._create_order()
        with self.assertRaises(ValidationError):
            services.refund_order(order)

    def test_refund_flips_order_and_payment(self):
        order = self._create_order()
        client().post(
            reverse('order-mock-confirm', args=[order.id]), **auth(self.buyer)
        )
        order.refresh_from_db()

        refunded = services.refund_order(order)

        order.refresh_from_db()
        self.assertEqual(refunded.status, Order.Status.REFUNDED)
        self.assertEqual(order.status, Order.Status.REFUNDED)
        self.assertEqual(order.payment.status, Payment.Status.REFUNDED)

    def test_can_refund_in_progress_order(self):
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
        order.refresh_from_db()

        services.refund_order(order)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.REFUNDED)


class SimulationGatewayTests(OrderSetupMixin):
    def test_checkout_creates_simulation_session(self):
        client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        order = Order.objects.get(application=self.application)

        session = services.gateway().create_checkout_session(order)

        self.assertEqual(session['mode'], 'simulation')
        self.assertTrue(session['session_id'].startswith('sim_'))
        order.payment.refresh_from_db()
        self.assertEqual(order.payment.gateway, 'simulation')
        self.assertEqual(order.payment.gateway_session_id, session['session_id'])

    def test_simulation_webhook_acknowledges_quietly(self):
        self.assertIsNone(services.SimulationGateway().handle_webhook(None))


class StripeGatewayTests(OrderSetupMixin):
    def _create_order(self):
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 201)
        return Order.objects.get(application=self.application)

    def stub_stripe(self, event_type='checkout.session.completed', metadata=None):
        object_ = {'metadata': metadata or {}}
        if event_type == 'checkout.session.completed':
            object_['payment_intent'] = 'pi_test_1'

        class FakeWebhook:
            @staticmethod
            def construct_event(payload, signature, secret):
                return {'type': event_type, 'data': {'object': object_}}

        class FakeSession:
            id = 'cs_test_123'
            url = 'https://checkout.stripe.com/cs_test_123'

        class FakeStripe:
            class checkout:
                class Session:
                    @staticmethod
                    def create(**kwargs):
                        return FakeSession()

            Webhook = FakeWebhook

        return FakeStripe

    def test_checkout_creates_stripe_session(self):
        order = self._create_order()
        gateway = services.StripeGateway()
        with mock.patch.object(
            services.StripeGateway, '_client', return_value=self.stub_stripe()
        ):
            session = gateway.create_checkout_session(order)

        self.assertEqual(
            session,
            {
                'session_id': 'cs_test_123',
                'url': 'https://checkout.stripe.com/cs_test_123',
                'mode': 'stripe',
            },
        )
        order.payment.refresh_from_db()
        self.assertEqual(order.payment.gateway, 'stripe')
        self.assertEqual(order.payment.gateway_session_id, 'cs_test_123')

    def test_webhook_marks_order_paid(self):
        order = self._create_order()
        gateway = services.StripeGateway()
        request = mock.Mock(body=b'{}', headers={'Stripe-Signature': 'sig_test_1'})
        fake = self.stub_stripe(metadata={'order_id': str(order.id)})
        with mock.patch.object(services.StripeGateway, '_client', return_value=fake):
            gateway.handle_webhook(request)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(order.payment.status, Payment.Status.PAID)
        self.assertEqual(order.payment.gateway_charge_id, 'pi_test_1')

    def test_webhook_ignores_unrelated_events(self):
        order = self._create_order()
        gateway = services.StripeGateway()
        request = mock.Mock(body=b'{}', headers={'Stripe-Signature': 'sig'})
        with mock.patch.object(
            services.StripeGateway,
            '_client',
            return_value=self.stub_stripe(event_type='payment_intent.created'),
        ):
            gateway.handle_webhook(request)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PENDING_PAYMENT)


class MockConfirmConfigurationTests(OrderSetupMixin):
    def test_mock_confirm_disabled_when_stripe_configured(self):
        created = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(created.status_code, 201)
        order_id = created.json()['id']

        with mock.patch.object(services, 'CONFIGURED', True):
            response = client().post(
                reverse('order-mock-confirm', args=[order_id]), **auth(self.buyer)
            )

        self.assertEqual(response.status_code, 404)


class OrderGuardTests(OrderSetupMixin):
    def _create_order(self):
        response = client().post(
            reverse('order-list'),
            {'application': self.application.id},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(response.status_code, 201)
        return response.json()['id']

    def test_list_is_empty_for_user_without_profile(self):
        no_profile = make_player('noprofile2')
        response = client().get(reverse('order-list'), **auth(no_profile))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

    def test_buyer_role_filter(self):
        self._create_order()
        response = client().get(
            reverse('order-list'), {'role': 'buyer'}, **auth(self.provider)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

    def test_detail_404_for_user_without_profile(self):
        order_id = self._create_order()
        no_profile = make_player('noprofile3')
        response = client().get(
            reverse('order-detail', args=[order_id]), **auth(no_profile)
        )
        self.assertEqual(response.status_code, 404)

    def test_staff_cannot_cancel_participant_order(self):
        from apps.users.models import User

        staff = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='strong-pass-123',
        )
        staff.is_staff = True
        staff.email_verified = True
        staff.save()
        order_id = self._create_order()

        response = client().patch(
            reverse('order-detail', args=[order_id]),
            {'action': 'cancel'},
            content_type='application/json',
            **auth(staff),
        )

        self.assertEqual(response.status_code, 403)

    def test_provider_cannot_start_unpaid_order(self):
        order_id = self._create_order()
        response = client().patch(
            reverse('order-detail', args=[order_id]),
            {'action': 'start'},
            content_type='application/json',
            **auth(self.provider),
        )
        self.assertEqual(response.status_code, 400)

    def test_checkout_returns_400_when_gateway_fails(self):
        order_id = self._create_order()
        with mock.patch.object(
            services,
            'gateway',
            side_effect=RuntimeError('stripe unavailable'),
        ):
            response = client().post(
                reverse('order-checkout', args=[order_id]), **auth(self.buyer)
            )
        self.assertEqual(response.status_code, 400)

    def test_webhook_returns_400_when_processing_fails(self):
        gateway = mock.Mock()
        gateway.handle_webhook.side_effect = Exception('signature mismatch')
        with mock.patch.object(services, 'gateway', return_value=gateway):
            response = client().post(
                reverse('stripe-webhook'),
                {},
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 400)
