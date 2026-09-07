"""API tests for reports and moderation actions."""

from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.listings.models import Category, Listing, ListingModerationStatus
from apps.moderation.models import Report, ReportStatus, ReportTargetType
from apps.profiles.models import Profile


def bearer(user):
    return {
        'HTTP_AUTHORIZATION': f'Bearer {str(RefreshToken.for_user(user).access_token)}'
    }


class ModerationTestBase(TestCase):
    def make_user(self, username, email, **kwargs):
        from apps.users.models import User

        defaults = {'password': 'strong-pass-123', 'email_verified': True}
        defaults.update(kwargs)
        user = User.objects.create_user(
            username=username, email=email, password=defaults.pop('password')
        )
        for key, value in defaults.items():
            setattr(user, key, value)
        user.save()
        Profile.objects.create(user=user)
        return user

    def make_staff(self, username='mod'):
        from apps.users.models import User

        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='strong-pass-123',
        )
        user.is_staff = True
        user.email_verified = True
        user.save()
        Profile.objects.create(user=user)
        return user

    def make_listing(self, provider):
        category = Category.objects.create(name='Tutoring')
        return Listing.objects.create(
            provider=provider.profile,
            category=category,
            title='Python Tutoring',
            price='25.00',
        )


class ReportTests(ModerationTestBase):
    def test_user_files_report_against_listing(self):
        reporter = self.make_user('buyer', 'buyer@example.com')
        target_user = self.make_user('target', 'target@example.com')
        listing = self.make_listing(target_user)

        response = self.client.post(
            reverse('report-create'),
            {
                'target_type': ReportTargetType.LISTING,
                'target_id': listing.id,
                'reason': 'Spam',
                'description': 'Looks like spam.',
            },
            content_type='application/json',
            **bearer(reporter),
        )

        self.assertEqual(response.status_code, 201)
        report = Report.objects.get()
        self.assertEqual(report.reporter, reporter)
        self.assertEqual(report.target_type, ReportTargetType.LISTING)
        self.assertEqual(report.status, ReportStatus.PENDING)

    def test_duplicate_report_rejected(self):
        reporter = self.make_user('buyer', 'buyer@example.com')
        target_user = self.make_user('target', 'target@example.com')
        listing = self.make_listing(target_user)
        self.client.post(
            reverse('report-create'),
            {
                'target_type': ReportTargetType.LISTING,
                'target_id': listing.id,
                'reason': 'Spam',
            },
            content_type='application/json',
            **bearer(reporter),
        )
        response = self.client.post(
            reverse('report-create'),
            {
                'target_type': ReportTargetType.LISTING,
                'target_id': listing.id,
                'reason': 'Again',
            },
            content_type='application/json',
            **bearer(reporter),
        )
        self.assertEqual(response.status_code, 400)

    def test_report_requires_authentication(self):
        response = self.client.post(
            reverse('report-create'),
            {'target_type': ReportTargetType.USER, 'target_id': 1, 'reason': 'x'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_unknown_target_rejected(self):
        reporter = self.make_user('buyer', 'buyer@example.com')
        response = self.client.post(
            reverse('report-create'),
            {
                'target_type': ReportTargetType.LISTING,
                'target_id': 9999,
                'reason': 'Spam',
            },
            content_type='application/json',
            **bearer(reporter),
        )
        self.assertEqual(response.status_code, 400)

    def test_user_can_only_view_own_reports(self):
        reporter = self.make_user('buyer', 'buyer@example.com')
        other = self.make_user('other', 'other@example.com')
        target_user = self.make_user('target', 'target@example.com')
        report = Report.objects.create(
            reporter=other,
            target_type=ReportTargetType.USER,
            target_id=target_user.id,
            reason='Spam',
        )
        response = self.client.get(
            reverse('report-detail', args=[report.id]), **bearer(reporter)
        )
        self.assertEqual(response.status_code, 403)


class AdminModerationTests(ModerationTestBase):
    def test_only_staff_can_review_reports(self):
        reporter = self.make_user('buyer', 'buyer@example.com')
        target_user = self.make_user('target', 'target@example.com')
        report = Report.objects.create(
            reporter=reporter,
            target_type=ReportTargetType.USER,
            target_id=target_user.id,
            reason='Spam',
        )
        response = self.client.post(
            reverse('report-detail', args=[report.id]),
            {'action': 'resolve', 'admin_notes': 'verified'},
            content_type='application/json',
            **bearer(reporter),
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_resolves_report(self):
        reporter = self.make_user('buyer', 'buyer@example.com')
        staff = self.make_staff()
        target_user = self.make_user('target', 'target@example.com')
        report = Report.objects.create(
            reporter=reporter,
            target_type=ReportTargetType.USER,
            target_id=target_user.id,
            reason='Spam',
        )
        response = self.client.post(
            reverse('report-detail', args=[report.id]),
            {'action': 'resolve', 'admin_notes': 'reviewed and resolved'},
            content_type='application/json',
            **bearer(staff),
        )
        self.assertEqual(response.status_code, 200)
        report.refresh_from_db()
        self.assertEqual(report.status, ReportStatus.RESOLVED)
        self.assertEqual(report.reviewed_by, staff)

    def test_staff_suspends_user(self):
        staff = self.make_staff()
        target_user = self.make_user('target', 'target@example.com')
        response = self.client.post(
            reverse('moderation-user', args=[target_user.id]),
            {'action': 'suspend', 'reason': 'abuse'},
            content_type='application/json',
            **bearer(staff),
        )
        self.assertEqual(response.status_code, 200)
        target_user.refresh_from_db()
        self.assertFalse(target_user.is_active)

    def test_staff_reactivates_user(self):
        staff = self.make_staff()
        target_user = self.make_user('target', 'target@example.com')
        target_user.is_active = False
        target_user.save(update_fields=['is_active'])
        response = self.client.post(
            reverse('moderation-user', args=[target_user.id]),
            {'action': 'reactivate'},
            content_type='application/json',
            **bearer(staff),
        )
        self.assertEqual(response.status_code, 200)
        target_user.refresh_from_db()
        self.assertTrue(target_user.is_active)

    def test_non_staff_cannot_suspend(self):
        target_user = self.make_user('target', 'target@example.com')
        attacker = self.make_user('attacker', 'attacker@example.com')
        response = self.client.post(
            reverse('moderation-user', args=[target_user.id]),
            {'action': 'suspend'},
            content_type='application/json',
            **bearer(attacker),
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_suspends_listing(self):
        staff = self.make_staff()
        provider = self.make_user('provider', 'provider@example.com')
        listing = self.make_listing(provider)
        response = self.client.post(
            reverse('moderation-listing-detail', args=[listing.id]),
            {'action': 'suspend', 'note': 'Inappropriate content'},
            content_type='application/json',
            **bearer(staff),
        )
        self.assertEqual(response.status_code, 200)
        listing.refresh_from_db()
        self.assertEqual(listing.moderation_status, ListingModerationStatus.SUSPENDED)
        self.assertFalse(listing.is_active)

    def test_staff_removes_listing(self):
        staff = self.make_staff()
        provider = self.make_user('provider', 'provider@example.com')
        listing = self.make_listing(provider)
        response = self.client.post(
            reverse('moderation-listing-detail', args=[listing.id]),
            {'action': 'remove', 'note': 'Violates guidelines'},
            content_type='application/json',
            **bearer(staff),
        )
        self.assertEqual(response.status_code, 200)
        listing.refresh_from_db()
        self.assertEqual(listing.moderation_status, ListingModerationStatus.ARCHIVED)
        self.assertTrue(listing.is_archived)

    def test_staff_approves_listed_listing(self):
        staff = self.make_staff()
        provider = self.make_user('provider', 'provider@example.com')
        listing = self.make_listing(provider)
        response = self.client.post(
            reverse('moderation-listing-detail', args=[listing.id]),
            {'action': 'approve'},
            content_type='application/json',
            **bearer(staff),
        )
        self.assertEqual(response.status_code, 200)
        listing.refresh_from_db()
        self.assertEqual(listing.moderation_status, ListingModerationStatus.PUBLISHED)


class TargetResolutionTests(ModerationTestBase):
    def completed_order(self, buyer, provider):
        from apps.listings.services import accept_application, apply_to_listing
        from apps.orders.services import create_order

        listing = self.make_listing(provider)
        application = apply_to_listing(listing, buyer.profile, message='hi')
        accept_application(application)
        return create_order(application, buyer.profile)

    def file_report(self, reporter, target_type, target_id):
        return self.client.post(
            reverse('report-create'),
            {
                'target_type': target_type,
                'target_id': target_id,
                'reason': 'Spam',
            },
            content_type='application/json',
            **bearer(reporter),
        )

    def test_report_against_message_resolves_target_name(self):
        buyer = self.make_user('buyer', 'buyer@example.com')
        provider = self.make_user('provider', 'provider@example.com')
        order = self.completed_order(buyer, provider)
        from apps.messaging.models import Message

        message = Message.objects.create(
            thread=order.thread, sender=buyer.profile, body='hello'
        )

        response = self.file_report(buyer, ReportTargetType.MESSAGE, message.id)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['target_name'], f'Message {message.id}')

    def test_report_against_review_resolves_target_name(self):
        buyer = self.make_user('buyer', 'buyer@example.com')
        provider = self.make_user('provider', 'provider@example.com')
        order = self.completed_order(buyer, provider)
        from apps.reviews.models import Review

        review = Review.objects.create(
            order=order,
            reviewer=buyer.profile,
            reviewee=provider.profile,
            rating=4,
            comment='Fine.',
        )

        response = self.file_report(buyer, ReportTargetType.REVIEW, review.id)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['target_name'], f'Review {review.id} (4/5)')

    def test_report_against_user_resolves_username(self):
        reporter = self.make_user('reporter', 'reporter@example.com')
        target = self.make_user('target', 'target@example.com')

        response = self.file_report(reporter, ReportTargetType.USER, target.id)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['target_name'], target.username)

    def test_report_requires_a_profile(self):
        from apps.users.models import User

        no_profile = User.objects.create_user(
            username='ghost', email='ghost@example.com', password='strong-pass-123'
        )
        no_profile.email_verified = True
        no_profile.save(update_fields=['email_verified'])
        target = self.make_user('target', 'target2@example.com')

        response = self.file_report(no_profile, ReportTargetType.USER, target.id)

        self.assertEqual(response.status_code, 400)

    def test_unknown_listing_target_rejected(self):
        reporter = self.make_user('reporter2', 'reporter2@example.com')
        response = self.file_report(reporter, ReportTargetType.LISTING, 9999)
        self.assertEqual(response.status_code, 400)

    def test_unknown_message_target_rejected(self):
        reporter = self.make_user('reporter3', 'reporter3@example.com')
        response = self.file_report(reporter, ReportTargetType.MESSAGE, 9999)
        self.assertEqual(response.status_code, 400)

    def test_unknown_review_target_rejected(self):
        reporter = self.make_user('reporter4', 'reporter4@example.com')
        response = self.file_report(reporter, ReportTargetType.REVIEW, 9999)
        self.assertEqual(response.status_code, 400)


class StaffReportToolsTests(ModerationTestBase):
    def setUp(self):
        super().setUp()
        self.staff = self.make_staff()
        self.reporter = self.make_user('reporter', 'reporter@example.com')
        self.target = self.make_user('target', 'target@example.com')
        self.report = Report.objects.create(
            reporter=self.reporter,
            target_type=ReportTargetType.USER,
            target_id=self.target.id,
            reason='Spam',
        )

    def test_staff_lists_all_reports(self):
        response = self.client.get(reverse('report-list'), **bearer(self.staff))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.report.id, [r['id'] for r in response.json()['results']])

    def test_staff_filters_reports_by_status_and_target(self):
        Report.objects.create(
            reporter=self.reporter,
            target_type=ReportTargetType.LISTING,
            target_id=1,
            reason='Other',
        )
        base = reverse('report-list')

        pending = self.client.get(base, {'status': 'pending'}, **bearer(self.staff))
        self.assertEqual(len(pending.json()['results']), 2)

        listing = self.client.get(
            base, {'target_type': 'listing'}, **bearer(self.staff)
        )
        self.assertEqual(len(listing.json()['results']), 1)
        self.assertEqual(
            listing.json()['results'][0]['target_type'], ReportTargetType.LISTING
        )

    def test_user_lists_only_own_reports(self):
        other = self.make_user('other', 'other@example.com')
        Report.objects.create(
            reporter=other,
            target_type=ReportTargetType.USER,
            target_id=1,
            reason='Spam',
        )

        response = self.client.get(reverse('report-list'), **bearer(self.reporter))

        ids = [r['id'] for r in response.json()['results']]
        self.assertEqual(ids, [self.report.id])

    def test_staff_rejects_report(self):
        response = self.client.post(
            reverse('report-detail', args=[self.report.id]),
            {'action': 'reject', 'admin_notes': 'unsubstantiated'},
            content_type='application/json',
            **bearer(self.staff),
        )

        self.assertEqual(response.status_code, 200)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, ReportStatus.REJECTED)
        self.assertIsNotNone(self.report.resolved_at)

    def test_already_resolved_report_cannot_be_reviewed_again(self):
        self.report.resolve(actor=self.staff, status=ReportStatus.RESOLVED)
        response = self.client.post(
            reverse('report-detail', args=[self.report.id]),
            {'action': 'resolve'},
            content_type='application/json',
            **bearer(self.staff),
        )
        self.assertEqual(response.status_code, 400)

    def test_staff_can_read_any_report(self):
        response = self.client.get(
            reverse('report-detail', args=[self.report.id]), **bearer(self.staff)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.report.id)

    def test_user_moderation_with_reason_logs_admin_report(self):
        response = self.client.post(
            reverse('moderation-user', args=[self.target.id]),
            {'action': 'suspend', 'reason': 'abuse'},
            content_type='application/json',
            **bearer(self.staff),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Report.objects.filter(
                reporter=self.staff,
                target_type=ReportTargetType.USER,
                reason='admin_action',
            ).exists()
        )

    def test_listing_moderation_filters_by_status(self):
        provider = self.make_user('provider', 'provider@example.com')
        self.make_listing(provider)
        response = self.client.get(
            reverse('moderation-listing-list'),
            {'status': ListingModerationStatus.REJECTED},
            **bearer(self.staff),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])
