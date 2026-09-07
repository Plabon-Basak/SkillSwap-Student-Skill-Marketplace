"""Serializers for moderation and admin actions."""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.moderation.models import Report, ReportTargetType
from apps.users.serializers import UserSerializer


class ReviewedBySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)


class ReportSerializer(serializers.ModelSerializer):
    """Staff-facing view of a report."""

    reporter = UserSerializer(read_only=True)
    reviewed_by = ReviewedBySerializer(read_only=True)
    target_name = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'reporter',
            'target_type',
            'target_id',
            'target_name',
            'reason',
            'description',
            'status',
            'admin_notes',
            'reviewed_by',
            'resolved_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_target_name(self, obj):
        try:
            return _resolve_target_name(obj)
        except Exception:
            return None


def _resolve_target_name(report: Report):
    if report.target_type == ReportTargetType.USER:
        from apps.users.models import User

        return User.objects.get(id=report.target_id).username
    if report.target_type == ReportTargetType.LISTING:
        from apps.listings.models import Listing

        listing = Listing.objects.get(id=report.target_id)
        return listing.title
    if report.target_type == ReportTargetType.MESSAGE:
        from apps.messaging.models import Message

        message = Message.objects.get(id=report.target_id)
        return f'Message {message.pk}'
    if report.target_type == ReportTargetType.REVIEW:
        from apps.reviews.models import Review

        review = Review.objects.get(id=report.target_id)
        return f'Review {review.pk} ({review.rating}/5)'
    return None


class ReportCreateSerializer(serializers.Serializer):
    """A user files a report against a target."""

    target_type = serializers.ChoiceField(choices=ReportTargetType.choices)
    target_id = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=120)
    description = serializers.CharField(
        required=False, allow_blank=True, max_length=2000
    )

    def validate(self, attrs):
        target_type = attrs['target_type']
        target_id = attrs['target_id']
        if target_type == ReportTargetType.USER:
            from apps.users.models import User

            if not User.objects.filter(id=target_id).exists():
                raise serializers.ValidationError('Unknown user target.')
        elif target_type == ReportTargetType.LISTING:
            from apps.listings.models import Listing

            if not Listing.objects.filter(id=target_id).exists():
                raise serializers.ValidationError('Unknown listing target.')
        elif target_type == ReportTargetType.MESSAGE:
            from apps.messaging.models import Message

            if not Message.objects.filter(id=target_id).exists():
                raise serializers.ValidationError('Unknown message target.')
        elif target_type == ReportTargetType.REVIEW:
            from apps.reviews.models import Review

            if not Review.objects.filter(id=target_id).exists():
                raise serializers.ValidationError('Unknown review target.')
        return attrs


class AdminReportActionSerializer(serializers.Serializer):
    """Admins review a report and decide its outcome."""

    action = serializers.ChoiceField(choices=['resolve', 'reject'])
    admin_notes = serializers.CharField(
        required=False, allow_blank=True, max_length=2000
    )


class UserModerationSerializer(serializers.Serializer):
    """Admins suspend or reactivate a user."""

    action = serializers.ChoiceField(choices=['suspend', 'reactivate'])
    reason = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class ListingModerationSerializer(serializers.Serializer):
    """Admins approve, reject, suspend or remove a listing."""

    action = serializers.ChoiceField(choices=['approve', 'reject', 'suspend', 'remove'])
    note = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class AdminActionResultSerializer(serializers.Serializer):
    """Generic human-readable outcome returned by admin actions."""

    detail = serializers.CharField(read_only=True)
