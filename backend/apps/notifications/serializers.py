"""Serializers for notifications."""

from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'verb',
            'actor_username',
            'target_type',
            'target_id',
            'data',
            'is_read',
            'created_at',
        ]
        read_only_fields = fields


class UnreadCountSerializer(serializers.Serializer):
    """Simple counter payload, shared by notifications and threads."""

    count = serializers.IntegerField(read_only=True)


class MarkedReadSerializer(serializers.Serializer):
    """Number of notifications marked as read by a bulk action."""

    marked_read = serializers.IntegerField(read_only=True)
