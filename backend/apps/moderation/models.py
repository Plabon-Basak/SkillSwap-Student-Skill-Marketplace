"""Moderation: reports, user suspension and listing moderation.

A generic report can target a user, a listing, a message or a review. The
target is stored as a polymorphic (type, id) pair so a single index can cover
every reportable entity without separate tables or a fragile messy
generic-foreign-key dependency.
"""

from django.db import models
from django.utils import timezone


class ReportTargetType(models.TextChoices):
    USER = 'user', 'User'
    LISTING = 'listing', 'Listing'
    MESSAGE = 'message', 'Message'
    REVIEW = 'review', 'Review'


class ReportStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    REVIEWING = 'reviewing', 'Reviewing'
    RESOLVED = 'resolved', 'Resolved'
    REJECTED = 'rejected', 'Rejected'


class Report(models.Model):
    """A user's complaint about another user, a listing, message or review."""

    reporter = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='reports_made'
    )
    target_type = models.CharField(max_length=16, choices=ReportTargetType.choices)
    target_id = models.PositiveBigIntegerField()
    reason = models.CharField(max_length=120)
    description = models.TextField(max_length=2000, blank=True)
    status = models.CharField(
        max_length=12, choices=ReportStatus.choices, default=ReportStatus.PENDING
    )
    admin_notes = models.TextField(max_length=2000, blank=True)
    reviewed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_reviewed',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'moderation_report'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['reporter']),
        ]

    def __str__(self):
        return f'Report {self.pk} ({self.target_type}:{self.target_id})'

    def resolve(self, *, actor, status, admin_notes=''):
        self.status = status
        self.admin_notes = admin_notes
        self.reviewed_by = actor
        self.resolved_at = timezone.now()
        self.save(
            update_fields=[
                'status',
                'admin_notes',
                'reviewed_by',
                'resolved_at',
                'updated_at',
            ]
        )
