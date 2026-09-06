"""Tests for student profiles: creation, editing, privacy and authorization."""

import io

from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework_simplejwt.tokens import RefreshToken

from apps.profiles.models import Profile, Skill
from apps.users.models import User


def make_user(username='alice', verified=True, **kwargs):
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


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {str(refresh.access_token)}'}


def profile_payload(**overrides):
    payload = {
        'first_name': 'Alice',
        'last_name': 'Johnson',
        'university': 'Example University',
        'department': 'Computer Science',
        'bio': 'Python tutor and web developer.',
        'location': 'New York',
        'experience_years': 2,
        'skills': ['Python', 'Web Development'],
        'is_searchable': True,
    }
    payload.update(overrides)
    return payload


def make_png_bytes(name='avatar.png', color=(10, 20, 30)):
    buf = io.BytesIO()
    Image.new('RGB', (64, 64), color).save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


class ProfileAuthTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()

    def test_create_requires_authentication(self):
        response = self.client.post(
            reverse('profile-me'), {}, content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)

    def test_create_requires_verified_email(self):
        user = make_user(verified=False)

        response = self.client.post(
            reverse('profile-me'),
            profile_payload(),
            content_type='application/json',
            **auth(user),
        )

        self.assertEqual(response.status_code, 403)


class ProfileCrudTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.user = make_user()
        self.headers = auth(self.user)

    def test_create_profile(self):
        response = self.client.post(
            reverse('profile-me'),
            profile_payload(),
            content_type='application/json',
            **self.headers,
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['username'], 'alice')
        self.assertEqual(data['email'], 'alice@example.com')
        self.assertEqual(data['university'], 'Example University')
        self.assertCountEqual(
            [s['name'] for s in data['skills']], ['Python', 'Web Development']
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Alice')

    def test_create_duplicate_profile_conflicts(self):
        self.client.post(
            reverse('profile-me'),
            profile_payload(),
            content_type='application/json',
            **self.headers,
        )

        response = self.client.post(
            reverse('profile-me'),
            profile_payload(),
            content_type='application/json',
            **self.headers,
        )

        self.assertEqual(response.status_code, 409)

    def test_get_own_profile(self):
        self.client.post(
            reverse('profile-me'),
            profile_payload(),
            content_type='application/json',
            **self.headers,
        )

        response = self.client.get(reverse('profile-me'), **self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.json())

    def test_get_own_profile_missing_returns_404(self):
        response = self.client.get(reverse('profile-me'), **self.headers)

        self.assertEqual(response.status_code, 404)

    def test_update_profile_partial(self):
        self.client.post(
            reverse('profile-me'),
            profile_payload(),
            content_type='application/json',
            **self.headers,
        )

        response = self.client.patch(
            reverse('profile-me'),
            {'university': 'Updated University', 'skills': ['Design']},
            content_type='application/json',
            **self.headers,
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['university'], 'Updated University')
        self.assertEqual([s['name'] for s in data['skills']], ['Design'])

    def test_update_rejects_oversized_bio(self):
        self.client.post(
            reverse('profile-me'),
            profile_payload(),
            content_type='application/json',
            **self.headers,
        )

        response = self.client.patch(
            reverse('profile-me'),
            {'bio': 'x' * 501},
            content_type='application/json',
            **self.headers,
        )

        self.assertEqual(response.status_code, 400)

    def test_update_without_profile_returns_404(self):
        response = self.client.patch(
            reverse('profile-me'),
            {'bio': 'hi'},
            content_type='application/json',
            **self.headers,
        )

        self.assertEqual(response.status_code, 404)


class ProfileAvatarTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.user = make_user()
        self.headers = auth(self.user)

    def test_upload_valid_avatar(self):
        response = self.client.post(
            reverse('profile-me'),
            {'bio': 'hello', 'avatar': make_png_bytes()},
            format='multipart',
            **self.headers,
        )

        self.assertEqual(response.status_code, 201)
        profile = Profile.objects.get(user=self.user)
        self.assertTrue(profile.avatar.name.startswith('avatars/'))

    def test_reject_non_image_avatar(self):
        bad = SimpleUploadedFile(
            'avatar.png', b'this is not an image', content_type='text/plain'
        )
        response = self.client.post(
            reverse('profile-me'),
            {'bio': 'hello', 'avatar': bad},
            format='multipart',
            **self.headers,
        )

        self.assertEqual(response.status_code, 400)


class VerifiedBadgeTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.user = make_user()
        self.headers = auth(self.user)
        self.client.post(
            reverse('profile-me'),
            profile_payload(),
            content_type='application/json',
            **self.headers,
        )

    def test_non_staff_cannot_self_verify(self):
        response = self.client.patch(
            reverse('profile-me'),
            {'is_verified_student': True},
            content_type='application/json',
            **self.headers,
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Profile.objects.get(user=self.user).is_verified_student)

    def test_staff_can_verify(self):
        staff = make_user(username='staff')
        staff.is_staff = True
        staff.save(update_fields=['is_staff'])
        self.client.post(
            reverse('profile-me'),
            profile_payload(),
            content_type='application/json',
            **auth(staff),
        )

        response = self.client.patch(
            reverse('profile-me'),
            {'is_verified_student': True},
            content_type='application/json',
            **auth(staff),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.get(user=staff).is_verified_student)


class ProfilePrivacyTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.seller = make_user(username='seller')
        self.client.post(
            reverse('profile-me'),
            profile_payload(university='Uni A'),
            content_type='application/json',
            **auth(self.seller),
        )
        self.hidden = make_user(username='hidden')
        self.client.post(
            reverse('profile-me'),
            profile_payload(university='Uni B', is_searchable=False),
            content_type='application/json',
            **auth(self.hidden),
        )

    def test_public_list_excludes_email(self):
        response = self.client.get(reverse('profile-list'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        for item in payload['results']:
            self.assertNotIn('email', item)
        usernames = {item['username'] for item in payload['results']}
        self.assertIn('seller', usernames)
        self.assertNotIn('hidden', usernames)

    def test_public_detail_accessible_by_username(self):
        response = self.client.get(reverse('profile-detail', args=['seller']))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'seller')
        self.assertNotIn('email', response.json())

    def test_public_detail_hides_non_searchable(self):
        response = self.client.get(reverse('profile-detail', args=['hidden']))

        self.assertEqual(response.status_code, 404)

    def test_keyword_search(self):
        response = self.client.get(reverse('profile-list'), {'q': 'tutor'})

        usernames = {u['username'] for u in response.json()['results']}
        self.assertIn('seller', usernames)

    def test_university_filter(self):
        response = self.client.get(reverse('profile-list'), {'university': 'Uni A'})

        usernames = {u['username'] for u in response.json()['results']}
        self.assertEqual(usernames, {'seller'})

    def test_skill_filter(self):
        response = self.client.get(reverse('profile-list'), {'skill': 'python'})

        usernames = {u['username'] for u in response.json()['results']}
        self.assertIn('seller', usernames)


class SkillListTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()

    def test_skills_can_be_searched(self):
        Skill.objects.create(name='Python')
        Skill.objects.create(name='Photography')

        response = self.client.get(reverse('skill-list'), {'search': 'photo'})

        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Photography')
