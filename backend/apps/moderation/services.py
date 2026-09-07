"""Business logic for reports and moderation actions."""

from rest_framework.exceptions import ValidationError

from apps.moderation.models import Report, ReportStatus


def create_report(
    *, reporter, target_type, target_id, reason, description=''
) -> Report:
    """File a report. A user may only report a target once while open."""
    if Report.objects.filter(
        reporter=reporter,
        target_type=target_type,
        target_id=target_id,
        status__in=[ReportStatus.PENDING, ReportStatus.REVIEWING],
    ).exists():
        raise ValidationError('You have already reported this item.')
    return Report.objects.create(
        reporter=reporter,
        target_type=target_type,
        target_id=target_id,
        reason=reason,
        description=description,
    )


def review_report(*, report: Report, actor, action: str, admin_notes='') -> Report:
    status = ReportStatus.RESOLVED if action == 'resolve' else ReportStatus.REJECTED
    if report.status in (ReportStatus.RESOLVED, ReportStatus.REJECTED):
        raise ValidationError('This report has already been resolved.')
    report.resolve(actor=actor, status=status, admin_notes=admin_notes)
    return report
