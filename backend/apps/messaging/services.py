"""Thread and message operations, including participant notification."""

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.messaging.models import Message, Thread
from apps.notifications.services import notify


def create_thread_for_order(order) -> Thread:
    """A conversation is created for every order; idempotent per order."""
    thread, _ = Thread.objects.get_or_create(
        order=order,
        defaults={
            'buyer': order.buyer,
            'provider': order.provider,
        },
    )
    return thread


def is_participant(thread: Thread, profile) -> bool:
    return profile is not None and profile.id in (thread.buyer_id, thread.provider_id)


def send_message(thread: Thread, sender, *, body: str) -> Message:
    if not is_participant(thread, sender):
        raise ValidationError('Only participants of this order may send messages.')
    message = Message.objects.create(thread=thread, sender=sender, body=body)
    thread.last_message_at = message.created_at
    thread.save(update_fields=['last_message_at', 'updated_at'])

    other = thread.other_participant(sender)
    notify(
        recipient=other.user,
        actor=sender.user,
        verb='new_message',
        target_type='thread',
        target_id=thread.id,
        data={'order_id': thread.order_id},
    )
    return message


def mark_thread_read(thread: Thread, profile):
    """Mark every inbound message in the thread as read for the reader."""
    return (
        Message.objects.filter(thread=thread, is_read=False)
        .exclude(sender=profile)
        .update(is_read=True, read_at=timezone.now())
    )


def unread_count_for(thread: Thread, profile) -> int:
    return (
        Message.objects.filter(thread=thread, is_read=False)
        .exclude(sender=profile)
        .count()
    )
