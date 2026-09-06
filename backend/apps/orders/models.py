"""Orders and payments for accepted service applications."""

from django.db import models


class Order(models.Model):
    """A binding agreement once an application has been accepted.

    The lifecycle is linear: pending payment -> paid -> in progress ->
    completed. Cancellation is only possible while payment is still pending.
    """

    class Status(models.TextChoices):
        PENDING_PAYMENT = 'pending_payment', 'Pending payment'
        PAID = 'paid', 'Paid'
        IN_PROGRESS = 'in_progress', 'In progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'

    application = models.OneToOneField(
        'listings.Application',
        on_delete=models.PROTECT,
        related_name='order',
    )
    buyer = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='orders_as_buyer'
    )
    provider = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='orders_as_provider'
    )
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    note = models.TextField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['provider', 'status']),
        ]

    def __str__(self):
        return f'Order {self.pk} ({self.buyer.user.username} <- {self.listing_id})'


class Payment(models.Model):
    """The payment record attached to an order."""

    class Status(models.TextChoices):
        CREATED = 'created', 'Created'
        PAID = 'paid', 'Paid'
        REFUNDED = 'refunded', 'Refunded'
        FAILED = 'failed', 'Failed'

    order = models.OneToOneField(
        Order, on_delete=models.PROTECT, related_name='payment'
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.CREATED
    )
    gateway = models.CharField(max_length=20, default='stripe')
    gateway_session_id = models.CharField(max_length=255, blank=True)
    gateway_charge_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment {self.pk} ({self.status})'
