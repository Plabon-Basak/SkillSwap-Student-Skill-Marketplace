"""Creating and acknowledging notifications."""

from django.utils import timezone

from apps.notifications.models import Notification


def notify(*, recipient, verb, actor=None, target_type='', target_id=None, data=None):
    """Create a notification; the returned object is unread by default."""
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        target_type=target_type,
        target_id=target_id,
        data=data or {},
    )


def mark_notification_read(notification):
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save(update_fields=['is_read', 'read_at'])
    return notification


def unread_count_for(user) -> int:
    return Notification.objects.filter(recipient=user, is_read=False).count()
