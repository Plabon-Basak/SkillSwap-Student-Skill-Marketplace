"""Serializers for reviews."""

from rest_framework import serializers

from apps.listings.serializers import ProviderSummarySerializer
from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = ProviderSummarySerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'order',
            'reviewer',
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = ['id', 'order', 'reviewer', 'created_at']


class ReviewCreateSerializer(serializers.Serializer):
    order = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=1000)
