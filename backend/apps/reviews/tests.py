"""Tests for reviews and ratings."""

from decimal import Decimal

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.listings.models import Category
from apps.listings.services import accept_application, apply_to_listing
from apps.notifications.models import Notification
from apps.orders.models import Order
from apps.profiles.models import Profile
from apps.reviews import services
from apps.reviews.models import Review


def make_player(username='alice', verified=True, **kwargs):
    from apps.users.models import User

    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='strong-pass-123',
        **kwargs,
    )
    if verified:
        user.email_verified = True
        user.save(update_fields=['email_verified'])
    return user


def make_profile(user, **kwargs):
    profile_kwargs = {'university': 'Example U', 'bio': 'tutor'}
    profile_kwargs.update(kwargs)
    return Profile.objects.create(user=user, **profile_kwargs)


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}


def client():
    from django.test import Client as DjangoClient

    return DjangoClient()


def make_category(name='Tutoring'):
    category, _ = Category.objects.get_or_create(name=name)
    return category


def make_listing(provider_user):
    response = client().post(
        reverse('listing-list'),
        {
            'title': f'{provider_user.username} math help',
            'description': 'Weekly 1:1 sessions.',
            'price': '50.00',
            'category': make_category().slug,
            'skills': ['Mathematics'],
            'delivery_time_days': 7,
            'is_remote': True,
        },
        content_type='application/json',
        **auth(provider_user),
    )
    assert response.status_code == 201, response.content
    from apps.listings.models import Listing

    return Listing.objects.get(slug=response.json()['slug'])


def completed_order(provider_user, buyer_user):
    """Accept, order, pay and complete; returns the Order instance."""
    buyer_profile = Profile.objects.get(user=buyer_user)
    listing = make_listing(provider_user)
    application = apply_to_listing(listing, buyer_profile)
    accept_application(application)
    response = client().post(
        reverse('order-list'),
        {'application': application.id},
        content_type='application/json',
        **auth(buyer_user),
    )
    assert response.status_code == 201, response.content
    order = Order.objects.get(application=application)
    client().post(reverse('order-mock-confirm', args=[order.id]), **auth(buyer_user))
    client().patch(
        reverse('order-detail', args=[order.id]),
        {'action': 'start'},
        content_type='application/json',
        **auth(provider_user),
    )
    client().patch(
        reverse('order-detail', args=[order.id]),
        {'action': 'complete'},
        content_type='application/json',
        **auth(provider_user),
    )
    order.refresh_from_db()
    return order


class ReviewSetupMixin(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.provider = make_player('provider')
        make_profile(self.provider, bio='pro provider')
        self.buyer = make_player('buyer')
        self.buyer_profile = make_profile(self.buyer)
        self.order = completed_order(self.provider, self.buyer)

    def _review(self, **overrides):
        payload = {
            'order': self.order.id,
            'rating': 5,
            'comment': 'Great tutor.',
        }
        payload.update(overrides)
        return client().post(
            reverse('review-create'),
            payload,
            content_type='application/json',
            **auth(self.buyer),
        )


class ReviewCreationTests(ReviewSetupMixin):
    def test_create_review_success(self):
        response = self._review()
        self.assertEqual(response.status_code, 201)
        review = Review.objects.get(order=self.order)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.reviewer, self.buyer_profile)
        self.assertEqual(review.reviewee, self.provider.profile)

    def test_notifies_provider(self):
        self._review()
        n = Notification.objects.get(recipient=self.provider, verb='new_review')
        self.assertEqual(n.data['rating'], 5)

    def test_only_buyer_can_review(self):
        stranger = make_player('stranger')
        make_profile(stranger)
        response = client().post(
            reverse('review-create'),
            {'order': self.order.id, 'rating': 5},
            content_type='application/json',
            **auth(stranger),
        )
        # stranger is not the buyer -> order endpoint 403 (view-level guard)
        self.assertEqual(response.status_code, 403)

    def test_provider_cannot_review_own_order(self):
        response = self._review()
        self.assertEqual(response.status_code, 201)
        second = client().post(
            reverse('review-create'),
            {'order': self.order.id, 'rating': 4},
            content_type='application/json',
            **auth(self.buyer),
        )
        self.assertEqual(second.status_code, 400)

    def test_cannot_review_incomplete_order(self):
        buyer2 = make_player('buyer2')
        make_profile(buyer2)
        listing = make_listing(self.provider)
        application = apply_to_listing(listing, buyer2.profile)
        accept_application(application)
        # order created but not completed
        response = client().post(
            reverse('order-list'),
            {'application': application.id},
            content_type='application/json',
            **auth(buyer2),
        )
        self.assertEqual(response.status_code, 201)
        paid = client().post(
            reverse('order-mock-confirm', args=[application.order.id]),
            **auth(buyer2),
        )
        self.assertEqual(paid.status_code, 200)
        attempt = client().post(
            reverse('review-create'),
            {'order': application.order.id, 'rating': 4},
            content_type='application/json',
            **auth(buyer2),
        )
        self.assertEqual(attempt.status_code, 400)

    def test_invalid_rating_rejected(self):
        response = self._review(rating=0)
        self.assertEqual(response.status_code, 400)

    def test_requires_auth(self):
        response = client().post(
            reverse('review-create'),
            {'order': self.order.id, 'rating': 5},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)


class RatingAggregateTests(ReviewSetupMixin):
    def test_profile_shows_rating_aggregate(self):
        self._review(rating=5)
        detail = client().get(reverse('profile-detail', args=[self.provider.username]))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()['rating_count'], 1)
        self.assertEqual(detail.json()['rating_average'], float(Decimal('5.0')))

    def test_profile_list_annotates_ratings(self):
        self._review(rating=4)
        listing = client().get(reverse('profile-list')).json()['results']
        provider_entry = next(
            (p for p in listing if p['username'] == self.provider.username), None
        )
        self.assertIsNotNone(provider_entry)
        self.assertEqual(provider_entry['rating_count'], 1)
        self.assertAlmostEqual(provider_entry['rating_average'], 4.0, places=2)


class ProfileReviewsTests(ReviewSetupMixin):
    def test_public_reviews_endpoint(self):
        self._review(rating=5, comment='Excellent session.')
        response = client().get(
            reverse('profile-reviews', args=[self.provider.username])
        )
        self.assertEqual(response.status_code, 200)
        reviews = response.json()['results']
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['rating'], 5)
        self.assertEqual(reviews[0]['comment'], 'Excellent session.')

    def test_review_list_requires_no_auth(self):
        self._review()
        response = client().get(
            reverse('profile-reviews', args=[self.provider.username])
        )
        self.assertEqual(response.status_code, 200)

    def test_unknown_profile_reviews_404(self):
        response = client().get(reverse('profile-reviews', args=['nobody']))
        self.assertEqual(response.status_code, 404)


class ReviewServiceTests(ReviewSetupMixin):
    def test_service_rejects_non_buyer_reviewer(self):
        stranger = make_player('stranger')
        stranger_profile = make_profile(stranger)
        with self.assertRaises(ValidationError):
            services.create_review(
                order=self.order,
                reviewer=stranger_profile,
                rating=5,
                comment='Snooping.',
            )

    def test_rating_for_profile_aggregates(self):
        self._review(rating=5)
        result = services.rating_for_profile(self.provider.profile)
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['average'], float(Decimal('5.0')))

    def test_rating_aggregate_for_profiles_annotates(self):
        self._review(rating=4)
        qs = services.rating_aggregate_for_profiles(
            Profile.objects.filter(id=self.provider.profile.id)
        )
        profile = qs.get()
        self.assertEqual(profile.rating_count, 1)
        self.assertAlmostEqual(float(profile.rating_average), 4.0, places=2)
