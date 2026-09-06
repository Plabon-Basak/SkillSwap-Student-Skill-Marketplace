"""Serializers for threads and messages."""

from rest_framework import serializers

from apps.listings.serializers import ProviderSummarySerializer
from apps.messaging.models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = ProviderSummarySerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'body', 'is_read', 'created_at']


class ThreadSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(source='order.id', read_only=True)
    buyer = ProviderSummarySerializer(read_only=True)
    provider = ProviderSummarySerializer(read_only=True)
    last_message_at = serializers.DateTimeField(read_only=True)
    unread_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

    def get_unread_count(self, thread):
        from apps.messaging.services import unread_count_for

        return unread_count_for(thread, self.context.get('profile'))
