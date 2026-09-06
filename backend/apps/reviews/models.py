"""Text plus a star rating given by a buyer about a completed order."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """A buyer's evaluation of a delivered, completed order."""

    order = models.OneToOneField(
        'orders.Order', on_delete=models.CASCADE, related_name='review'
    )
    reviewer = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='reviews_written'
    )
    reviewee = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='reviews_received'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['reviewee', '-created_at'])]

    def __str__(self):
        return f'Review {self.pk} ({self.rating}/5) for {self.reviewee_id}'
