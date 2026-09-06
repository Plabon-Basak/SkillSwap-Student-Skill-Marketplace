"""Tests for marketplace listings, categories and applications."""

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.listings.models import Application, Category, Listing
from apps.profiles.models import Profile, Skill
from apps.users.models import User


def make_player(username='alice', verified=True, **kwargs):
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


def make_listing(username='alice', **overrides):
    user = make_player(username)
    make_profile(user)
    payload = {
        'title': f'{username} math help',
        'description': 'Weekly 1:1 sessions.',
        'price': '25',
        'category': make_category().slug,
        'skills': ['Mathematics'],
        'delivery_time_days': 7,
        'is_remote': True,
    }
    payload.update(overrides)
    response = client().post(
        reverse('listing-list'), payload, content_type='application/json', **auth(user)
    )
    assert response.status_code == 201, response.content
    return response.json(), user


def listing_payload(**overrides):
    payload = {
        'title': 'Python tutoring package',
        'description': 'Three 1:1 sessions covering fundamentals.',
        'price': '45.00',
        'currency': 'USD',
        'skills': ['Python', 'Teaching'],
        'delivery_time_days': 5,
        'is_remote': True,
        'location': 'Boston',
    }
    payload.update(overrides)
    return payload


class ListingCreationTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.user = make_player()
        self.profile = make_profile(self.user)
        self.headers = auth(self.user)

    def test_create_requires_authentication(self):
        response = client().post(
            reverse('listing-list'), listing_payload(), content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)

    def test_create_requires_verified_email(self):
        unverified = make_player(username='unverified', verified=False)

        response = client().post(
            reverse('listing-list'),
            listing_payload(),
            content_type='application/json',
            **auth(unverified),
        )

        self.assertEqual(response.status_code, 403)

    def test_create_requires_profile(self):
        profileless = make_player(username='noprofile')

        response = client().post(
            reverse('listing-list'),
            listing_payload(),
            content_type='application/json',
            **auth(profileless),
        )

        self.assertEqual(response.status_code, 400)

    def test_create_listing_success(self):
        response = client().post(
            reverse('listing-list'),
            listing_payload(),
            content_type='application/json',
            **self.headers,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['title'], 'Python tutoring package')
        self.assertEqual(data['provider']['username'], 'alice')
        self.assertTrue(data['slug'])
        self.assertEqual(data['price'], '45.00')
        self.assertCountEqual(
            [s['name'] for s in data['skills']], ['Python', 'Teaching']
        )

    def test_create_with_category_by_slug(self):
        category = make_category('Tutoring')

        response = client().post(
            reverse('listing-list'),
            listing_payload(category=category.slug),
            content_type='application/json',
            **self.headers,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['category']['slug'], 'tutoring')

    def test_create_rejects_negative_price(self):
        response = client().post(
            reverse('listing-list'),
            listing_payload(price='-5'),
            content_type='application/json',
            **self.headers,
        )

        self.assertEqual(response.status_code, 400)


class ListingReadTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.listing_data, self.seller = make_listing('seller')
        self.listing = Listing.objects.get(slug=self.listing_data['slug'])

    def test_public_list_shows_active(self):
        response = client().get(reverse('listing-list'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        item = payload['results'][0]
        self.assertIn('description', item)
        self.assertNotIn('email', item['provider'])

    def test_keyword_search(self):
        response = client().get(reverse('listing-list'), {'q': 'tutoring'})

        self.assertEqual(response.json()['count'], 1)

    def test_skill_filter(self):
        Skill.objects.create(name='Flute')

        response = client().get(reverse('listing-list'), {'skill': 'flute'})

        self.assertEqual(response.json()['count'], 0)

    def test_categorical_filter(self):
        response = client().get(reverse('listing-list'), {'category': 'tutoring'})

        self.assertEqual(response.json()['count'], 1)

    def test_price_range_filter(self):
        response = client().get(reverse('listing-list'), {'max_price': '10'})

        self.assertEqual(response.json()['count'], 0)

    def test_detail_public(self):
        response = client().get(reverse('listing-detail', args=[self.listing.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['slug'], self.listing.slug)

    def test_archived_listing_hidden_from_public(self):
        self.listing.archive()

        response = client().get(reverse('listing-list'))

        self.assertEqual(response.json()['count'], 0)

    def test_slug_auto_uniquified(self):
        listing_two = Listing.objects.create(
            provider=make_profile(make_player(username='other')),
            title=self.listing.title,
            price='10',
        )

        self.assertNotEqual(listing_two.slug, self.listing.slug)

    def test_provider_listing_filter(self):
        client().post(
            reverse('listing-list'),
            listing_payload(title='Second one'),
            content_type='application/json',
            **auth(self.seller),
        )

        response = client().get(reverse('listing-list'), {'provider': 'seller'})

        self.assertEqual(response.json()['count'], 2)


class ListingEditTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.data, self.seller = make_listing('seller')
        self.listing = Listing.objects.get(slug=self.data['slug'])
        self.seller_headers = auth(self.seller)

    def test_owner_can_patch(self):
        response = client().patch(
            reverse('listing-detail', args=[self.listing.slug]),
            {'price': '99'},
            content_type='application/json',
            **self.seller_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['price'], '99.00')

    def test_non_owner_cannot_patch(self):
        intruder = make_player(username='intruder')
        make_profile(intruder)

        response = client().patch(
            reverse('listing-detail', args=[self.listing.slug]),
            {'price': '1'},
            content_type='application/json',
            **auth(intruder),
        )

        self.assertEqual(response.status_code, 403)

    def test_owner_can_archive(self):
        response = client().delete(
            reverse('listing-detail', args=[self.listing.slug]), **self.seller_headers
        )

        self.assertEqual(response.status_code, 204)
        self.listing.refresh_from_db()
        self.assertTrue(self.listing.is_archived)

    def test_owner_sees_mine_including_archived(self):
        client().delete(
            reverse('listing-detail', args=[self.listing.slug]), **self.seller_headers
        )

        response = client().get(reverse('listing-mine'), **self.seller_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)

    def test_deactivation_hides_from_public(self):
        client().patch(
            reverse('listing-detail', args=[self.listing.slug]),
            {'is_active': False},
            content_type='application/json',
            **self.seller_headers,
        )

        response = client().get(reverse('listing-detail', args=[self.listing.slug]))

        self.assertEqual(response.status_code, 404)

    def test_owner_can_preview_own_inactive(self):
        client().patch(
            reverse('listing-detail', args=[self.listing.slug]),
            {'is_active': False},
            content_type='application/json',
            **self.seller_headers,
        )

        response = client().get(
            reverse('listing-detail', args=[self.listing.slug]), **self.seller_headers
        )

        self.assertEqual(response.status_code, 200)


class CategoryTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()

    def test_categories_listed(self):
        make_category('Tutoring')
        hidden = make_category('Hidden')
        hidden.is_active = False
        hidden.save()

        response = client().get(reverse('category-list'))

        self.assertEqual(response.status_code, 200)
        names = {item['name'] for item in response.json()}
        self.assertEqual(names, {'Tutoring'})


class ApplicationFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.data, self.seller = make_listing('seller')
        self.listing = Listing.objects.get(slug=self.data['slug'])
        self.seller_headers = auth(self.seller)
        self.buyer = make_player(username='buyer')
        self.buyer_profile = make_profile(self.buyer)
        self.buyer_headers = auth(self.buyer)
        self.applications_url = reverse(
            'listing-applications', args=[self.listing.slug]
        )

    def _apply(self, **overrides):
        payload = {'message': 'I need help with my midterm.', 'proposed_price': '20'}
        payload.update(overrides)
        return client().post(
            self.applications_url,
            payload,
            content_type='application/json',
            **self.buyer_headers,
        )

    def test_apply_success(self):
        response = self._apply()

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'pending')
        self.assertEqual(data['applicant']['username'], 'buyer')
        self.assertEqual(data['listing']['slug'], self.listing.slug)

    def test_apply_requires_profile(self):
        ghost = make_player(username='ghost')

        response = client().post(
            self.applications_url,
            {'message': 'hi'},
            content_type='application/json',
            **auth(ghost),
        )

        self.assertEqual(response.status_code, 400)

    def test_cannot_apply_to_own_listing(self):
        response = client().post(
            self.applications_url,
            {'message': 'myself'},
            content_type='application/json',
            **self.seller_headers,
        )

        self.assertEqual(response.status_code, 400)

    def test_duplicate_pending_application_rejected(self):
        self._apply()

        response = self._apply()

        self.assertEqual(response.status_code, 400)

    def test_apply_to_inactive_listing_rejected(self):
        client().patch(
            reverse('listing-detail', args=[self.listing.slug]),
            {'is_active': False},
            content_type='application/json',
            **self.seller_headers,
        )

        response = self._apply()

        self.assertEqual(response.status_code, 400)

    def test_provider_lists_applications(self):
        self._apply()

        response = client().get(self.applications_url, **self.seller_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_others_cannot_view_applications(self):
        outsider = make_player(username='outsider')
        make_profile(outsider)

        response = client().get(self.applications_url, **auth(outsider))

        self.assertEqual(response.status_code, 403)

    def test_buyer_accept_workflow(self):
        application_id = self._apply().json()['id']
        detail_url = reverse('application-detail', args=[application_id])

        response = client().patch(
            detail_url,
            {'action': 'accept'},
            content_type='application/json',
            **self.seller_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'accepted')
        application = Application.objects.get(id=application_id)
        self.assertIsNotNone(application.responded_at)

    def test_accepted_application_blocks_reapply(self):
        application_id = self._apply().json()['id']
        client().patch(
            reverse('application-detail', args=[application_id]),
            {'action': 'accept'},
            content_type='application/json',
            **self.seller_headers,
        )

        response = self._apply()

        self.assertEqual(response.status_code, 400)

    def test_rejected_application_allows_reapply(self):
        application_id = self._apply().json()['id']
        client().patch(
            reverse('application-detail', args=[application_id]),
            {'action': 'reject'},
            content_type='application/json',
            **self.seller_headers,
        )

        response = self._apply()

        self.assertEqual(response.status_code, 201)

    def test_buyer_can_withdraw(self):
        application_id = self._apply().json()['id']

        response = client().patch(
            reverse('application-detail', args=[application_id]),
            {'action': 'withdraw'},
            content_type='application/json',
            **self.buyer_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'withdrawn')

    def test_provider_cannot_withdraw(self):
        application_id = self._apply().json()['id']

        response = client().patch(
            reverse('application-detail', args=[application_id]),
            {'action': 'withdraw'},
            content_type='application/json',
            **self.seller_headers,
        )

        self.assertEqual(response.status_code, 403)

    def test_buyer_cannot_accept(self):
        application_id = self._apply().json()['id']

        response = client().patch(
            reverse('application-detail', args=[application_id]),
            {'action': 'accept'},
            content_type='application/json',
            **self.buyer_headers,
        )

        self.assertEqual(response.status_code, 403)

    def test_buyer_lists_own_applications(self):
        self._apply()

        response = client().get(reverse('application-mine'), **self.buyer_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)

    def test_cannot_respond_twice(self):
        application_id = self._apply().json()['id']
        client().patch(
            reverse('application-detail', args=[application_id]),
            {'action': 'accept'},
            content_type='application/json',
            **self.seller_headers,
        )

        response = client().patch(
            reverse('application-detail', args=[application_id]),
            {'action': 'reject'},
            content_type='application/json',
            **self.seller_headers,
        )

        self.assertEqual(response.status_code, 400)
