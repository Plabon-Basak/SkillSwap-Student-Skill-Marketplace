"""Per-order conversation threads between the buyer and provider."""

from django.db import models


class Thread(models.Model):
    """A private conversation between an order's buyer and provider."""

    order = models.OneToOneField(
        'orders.Order', on_delete=models.CASCADE, related_name='thread'
    )
    buyer = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='threads_as_buyer'
    )
    provider = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='threads_as_provider'
    )
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_message_at', '-created_at']

    def participants(self):
        return (self.buyer, self.provider)

    def other_participant(self, profile):
        return self.provider if profile.id == self.buyer.id else self.buyer

    def __str__(self):
        return f'Thread {self.pk} (order {self.order_id})'


class Message(models.Model):
    """A single message inside a thread."""

    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='sent_messages'
    )
    body = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['thread', 'created_at'])]

    def __str__(self):
        return f'Message {self.pk} in thread {self.thread_id}'
