"""Review workflow and profile rating aggregates."""

from django.db.models import Avg, Count
from rest_framework.exceptions import ValidationError

from apps.notifications.services import notify
from apps.orders.models import Order
from apps.reviews.models import Review


def create_review(*, order: Order, reviewer, rating: int, comment: str = '') -> Review:
    """A buyer reviews a completed order. One review per order."""
    if order.buyer != reviewer:
        raise ValidationError('Only the order buyer may write a review.')
    if order.status != Order.Status.COMPLETED:
        raise ValidationError('Only completed orders can be reviewed.')
    if Review.objects.filter(order=order).exists():
        raise ValidationError('This order already has a review.')
    review = Review.objects.create(
        order=order,
        reviewer=reviewer,
        reviewee=order.provider,
        rating=rating,
        comment=comment,
    )
    notify(
        recipient=order.provider.user,
        actor=reviewer.user,
        verb='new_review',
        target_type='order',
        target_id=order.id,
        data={'rating': rating, 'order_id': order.id},
    )
    return review


RatingAggregate = dict


def rating_aggregate_for_profiles(profiles):
    """Annotate a profile queryset with its review rating summary.

    Returns a copied queryset that adds `rating_average` and `rating_count`.
    """

    return profiles.annotate(
        rating_average=Avg('reviews_received__rating'),
        rating_count=Count('reviews_received'),
    )


def rating_for_profile(profile):
    agg = Review.objects.filter(reviewee=profile).aggregate(
        rating_average=Avg('rating'), rating_count=Count('id')
    )
    return {
        'average': agg['rating_average'],
        'count': agg['rating_count'],
    }
