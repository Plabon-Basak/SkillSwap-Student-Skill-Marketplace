"""Workflow logic for listing applications."""

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.listings.models import Application


def apply_to_listing(listing, applicant, *, message='', proposed_price=None):
    if listing.provider_id == applicant.id:
        raise ValidationError('You cannot apply to your own listing.')
    if Application.objects.filter(
        listing=listing, applicant=applicant, status=Application.Status.PENDING
    ).exists():
        raise ValidationError(
            'You already have a pending application for this listing.'
        )
    if Application.objects.filter(
        listing=listing, applicant=applicant, status=Application.Status.ACCEPTED
    ).exists():
        raise ValidationError('Your application for this listing was already accepted.')
    return Application.objects.create(
        listing=listing,
        applicant=applicant,
        message=message,
        proposed_price=proposed_price,
    )


def _respond(application, status):
    if application.status != Application.Status.PENDING:
        raise ValidationError('Only pending applications can be responded to.')
    application.status = status
    application.responded_at = timezone.now()
    application.save(update_fields=['status', 'responded_at', 'updated_at'])
    return application


def _notify_responded(application, verb):
    from apps.notifications.services import notify

    notify(
        recipient=application.applicant.user,
        actor=application.listing.provider.user,
        verb=verb,
        target_type='application',
        target_id=application.id,
        data={
            'listing_id': application.listing_id,
            'listing_title': application.listing.title,
        },
    )


def accept_application(application):
    if application.status != Application.Status.PENDING:
        raise ValidationError('Only pending applications can be accepted.')
    application = _respond(application, Application.Status.ACCEPTED)
    _notify_responded(application, 'application_accepted')
    return application


def reject_application(application):
    application = _respond(application, Application.Status.REJECTED)
    _notify_responded(application, 'application_rejected')
    return application


def withdraw_application(application):
    if application.status != Application.Status.PENDING:
        raise ValidationError('Only pending applications can be withdrawn.')
    application.status = Application.Status.WITHDRAWN
    application.save(update_fields=['status', 'updated_at'])
    from apps.notifications.services import notify

    notify(
        recipient=application.listing.provider.user,
        actor=application.applicant.user,
        verb='application_withdrawn',
        target_type='application',
        target_id=application.id,
        data={'listing_id': application.listing_id},
    )
    return application
