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


def accept_application(application):
    if application.status != Application.Status.PENDING:
        raise ValidationError('Only pending applications can be accepted.')
    return _respond(application, Application.Status.ACCEPTED)


def reject_application(application):
    return _respond(application, Application.Status.REJECTED)


def withdraw_application(application):
    if application.status != Application.Status.PENDING:
        raise ValidationError('Only pending applications can be withdrawn.')
    application.status = Application.Status.WITHDRAWN
    application.save(update_fields=['status', 'updated_at'])
    return application
