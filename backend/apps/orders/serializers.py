"""Serializers for orders and payments."""

from rest_framework import serializers

from apps.listings.serializers import (
    ListingSummarySerializer,
    ProviderSummarySerializer,
)


class OrderSerializer(serializers.Serializer):
    """Representation of an order; payer/payee data is the public profile."""

    id = serializers.IntegerField(read_only=True)
    application = serializers.IntegerField(source='application.id', read_only=True)
    listing = ListingSummarySerializer(read_only=True)
    buyer = ProviderSummarySerializer(read_only=True)
    provider = ProviderSummarySerializer(read_only=True)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    currency = serializers.CharField(read_only=True)
    note = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    paid_at = serializers.DateTimeField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    cancelled_at = serializers.DateTimeField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class OrderCreateSerializer(serializers.Serializer):
    application = serializers.IntegerField()
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)


class OrderActionSerializer(serializers.Serializer):
    """Explicit status transition applied in an order PATCH."""

    action = serializers.ChoiceField(choices=['cancel', 'start', 'complete'])


class CheckoutSessionSerializer(serializers.Serializer):
    """Result of opening a payment session; simulation in dev, Stripe in prod."""

    session_id = serializers.CharField(read_only=True)
    url = serializers.CharField(read_only=True)
    mode = serializers.ChoiceField(choices=['simulation', 'stripe'], read_only=True)
