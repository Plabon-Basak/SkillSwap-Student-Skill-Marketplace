"""Order lifecycle and payment gateway abstraction.

The gateway runs against real Stripe when STRIPE_API_KEY is configured and in
a simulation mode otherwise, so local development needs no credentials.
"""

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.listings.models import Application
from apps.messaging.services import create_thread_for_order
from apps.notifications.services import notify
from apps.orders.models import Order, Payment
from apps.profiles.models import Profile


def _ordered_price(application: Application):
    return application.proposed_price or application.listing.price


@transaction.atomic
def create_order(application: Application, buyer: Profile, *, note='') -> Order:
    listing = application.listing
    if application.status != Application.Status.ACCEPTED:
        raise ValidationError('Only accepted applications can be turned into an order.')
    if Order.objects.filter(application=application).exists():
        raise ValidationError('An order already exists for this application.')
    if listing.provider_id == buyer.id:
        raise ValidationError('You cannot order your own listing.')

    order = Order.objects.create(
        application=application,
        buyer=buyer,
        provider=listing.provider,
        listing=listing,
        price=_ordered_price(application),
        currency=listing.currency or 'USD',
        note=note or application.message,
    )
    Payment.objects.create(
        order=order,
        amount=order.price,
        currency=order.currency,
    )
    create_thread_for_order(order)
    notify(
        recipient=listing.provider.user,
        actor=buyer.user,
        verb='new_order',
        target_type='order',
        target_id=order.id,
        data={
            'price': str(order.price),
            'currency': order.currency,
            'listing_title': listing.title,
        },
    )
    return order


def _require_status(order: Order, statuses: tuple[str, ...], message: str):
    if order.status not in statuses:
        raise ValidationError(message)


def cancel_order(order: Order, cancelled_by=None) -> Order:
    """Buyer or provider may cancel while payment is still due."""
    _require_status(
        order,
        (Order.Status.PENDING_PAYMENT,),
        'Only orders awaiting payment can be cancelled.',
    )
    order.status = Order.Status.CANCELLED
    order.cancelled_at = timezone.now()
    order.save(update_fields=['status', 'cancelled_at', 'updated_at'])
    if cancelled_by is not None:
        counterpart = order.other_party(cancelled_by)
        notify(
            recipient=counterpart.user,
            actor=cancelled_by.user,
            verb='order_cancelled',
            target_type='order',
            target_id=order.id,
        )
    return order


def mark_order_paid(order: Order, *, gateway_charge_id='') -> Order:
    _require_status(
        order,
        (Order.Status.PENDING_PAYMENT,),
        'This order is not awaiting payment.',
    )
    order.status = Order.Status.PAID
    order.paid_at = timezone.now()
    order.save(update_fields=['status', 'paid_at', 'updated_at'])
    payment = order.payment
    payment.status = Payment.Status.PAID
    payment.gateway_charge_id = gateway_charge_id
    payment.save(update_fields=['status', 'gateway_charge_id', 'updated_at'])
    notify(
        recipient=order.provider.user,
        actor=order.buyer.user,
        verb='order_paid',
        target_type='order',
        target_id=order.id,
        data={'amount': str(order.price), 'currency': order.currency},
    )
    return order


def start_order(order: Order) -> Order:
    """The provider marks the job as being worked on."""
    _require_status(
        order,
        (Order.Status.PAID,),
        'Only paid orders can be started.',
    )
    order.status = Order.Status.IN_PROGRESS
    order.started_at = timezone.now()
    order.save(update_fields=['status', 'started_at', 'updated_at'])
    notify(
        recipient=order.buyer.user,
        actor=order.provider.user,
        verb='order_started',
        target_type='order',
        target_id=order.id,
    )
    return order


def complete_order(order: Order) -> Order:
    """The provider marks the service as delivered."""
    _require_status(
        order,
        (Order.Status.IN_PROGRESS, Order.Status.PAID),
        'Only started paid orders can be completed.',
    )
    order.status = Order.Status.COMPLETED
    order.completed_at = timezone.now()
    order.save(update_fields=['status', 'completed_at', 'updated_at'])
    notify(
        recipient=order.buyer.user,
        actor=order.provider.user,
        verb='order_completed',
        target_type='order',
        target_id=order.id,
    )
    return order


def refund_order(order: Order) -> Order:
    """Flip a paid order to refunded; used by moderation/admin."""
    _require_status(
        order,
        (Order.Status.PAID, Order.Status.IN_PROGRESS),
        'Only paid orders can be refunded.',
    )
    order.status = Order.Status.REFUNDED
    order.payment.status = Payment.Status.REFUNDED
    order.payment.save(update_fields=['status', 'updated_at'])
    order.save(update_fields=['status', 'updated_at'])
    return order


CONFIGURED = bool(settings.STRIPE_API_KEY)


class SimulationGateway:
    """Local, credential-free gateway used when Stripe is not configured."""

    mode = 'simulation'

    def create_checkout_session(self, order: Order):
        session_id = f'sim_{order.id}_{timezone.now().timestamp():.0f}'
        payment = order.payment
        payment.gateway = 'simulation'
        payment.gateway_session_id = session_id
        payment.save(update_fields=['gateway', 'gateway_session_id', 'updated_at'])
        return {
            'session_id': session_id,
            'url': f'/api/v1/orders/{order.id}/mock-confirm/',
            'mode': self.mode,
        }

    def handle_webhook(self, request):
        # Simulation mode emits no webhooks; acknowledge quietly.
        return None


class StripeGateway:
    """Real Stripe Checkout integration."""

    mode = 'stripe'

    def _client(self):
        import stripe  # Imported lazily so dev/test don't need the dependency wired.

        stripe.api_key = settings.STRIPE_API_KEY
        return stripe

    def create_checkout_session(self, order: Order):
        listing_title = order.listing.title if order.listing else f'Order {order.pk}'
        session = self._client().checkout.Session.create(
            mode='payment',
            line_items=[
                {
                    'price_data': {
                        'currency': order.currency.lower(),
                        'unit_amount': int(order.price * 100),
                        'product_data': {'name': listing_title},
                    },
                    'quantity': 1,
                }
            ],
            metadata={'order_id': str(order.id)},
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
        )
        payment = order.payment
        payment.gateway = 'stripe'
        payment.gateway_session_id = session.id
        payment.save(update_fields=['gateway', 'gateway_session_id', 'updated_at'])
        return {
            'session_id': session.id,
            'url': session.url,
            'mode': self.mode,
        }

    def handle_webhook(self, request):
        payload = request.body
        signature = request.headers.get('Stripe-Signature', '')
        event = self._client().Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session.get('metadata', {}).get('order_id')
            order = Order.objects.select_for_update().get(id=order_id)
            mark_order_paid(order, gateway_charge_id=session.get('payment_intent', ''))
        return None


def gateway():
    return StripeGateway() if CONFIGURED else SimulationGateway()
