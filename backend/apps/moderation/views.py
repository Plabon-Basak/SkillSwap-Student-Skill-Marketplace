"""API views for moderation: user reports, admin suspension and listing review."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from apps.listings.models import Listing
from apps.listings.serializers import ListingSerializer
from apps.moderation import services
from apps.moderation.models import Report
from apps.moderation.serializers import (
    AdminActionResultSerializer,
    AdminReportActionSerializer,
    ListingModerationSerializer,
    ReportCreateSerializer,
    ReportSerializer,
    UserModerationSerializer,
)
from apps.users.permissions import IsEmailVerified


class IsStaff(BasePermission):
    """Restrict the view to staff (moderators/admins)."""

    message = 'Staff access required.'

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )


class ReportCreateView(generics.GenericAPIView):
    """Any authenticated verified user files a report."""

    permission_classes = [IsAuthenticated, IsEmailVerified]
    serializer_class = ReportCreateSerializer

    @extend_schema(request=ReportCreateSerializer, responses=ReportSerializer)
    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return Response(
                {'detail': 'Create a profile before reporting.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = ReportCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            report = services.create_report(
                reporter=request.user,
                target_type=ser.validated_data['target_type'],
                target_id=ser.validated_data['target_id'],
                reason=ser.validated_data['reason'],
                description=ser.validated_data.get('description', ''),
            )
        except Exception as exc:
            return Response(
                {'detail': str(exc.detail[0])}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)


class ReportListView(generics.ListAPIView):
    """Staff lists and filters reports; users see their own reports."""

    serializer_class = ReportSerializer

    def get_permissions(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return []
        return [IsEmailVerified()]

    def get_queryset(self):
        qs = Report.objects.select_related('reporter', 'reviewed_by')
        if self.request.user.is_staff:
            params = self.request.query_params
            status_filter = params.get('status', '').strip()
            if status_filter:
                qs = qs.filter(status=status_filter)
            target_type = params.get('target_type', '').strip()
            if target_type:
                qs = qs.filter(target_type=target_type)
            return qs
        return qs.filter(reporter=self.request.user)


class ReportDetailView(generics.GenericAPIView):
    """A single report; staff review it, the reporter reads it."""

    serializer_class = ReportSerializer

    def _report(self):
        return get_object_or_404(
            Report.objects.select_related('reporter', 'reviewed_by'),
            pk=self.kwargs['pk'],
        )

    def get_permissions(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return []
        return [IsEmailVerified()]

    def get(self, request, *args, **kwargs):
        report = self._report()
        if not request.user.is_staff and report.reporter_id != request.user.id:
            return Response(
                {'detail': 'You may only view your own reports.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(ReportSerializer(report).data)

    @extend_schema(request=AdminReportActionSerializer, responses=ReportSerializer)
    def post(self, request, *args, **kwargs):
        report = self._report()
        if not request.user.is_staff:
            return Response(
                {'detail': 'Staff access required.'}, status=status.HTTP_403_FORBIDDEN
            )
        ser = AdminReportActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            report = services.review_report(
                report=report,
                actor=request.user,
                action=ser.validated_data['action'],
                admin_notes=ser.validated_data.get('admin_notes', ''),
            )
        except Exception as exc:
            return Response(
                {'detail': str(exc.detail[0])}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(ReportSerializer(report).data)


class UserModerationView(generics.GenericAPIView):
    """Staff suspend or reactivate a user account."""

    permission_classes = [IsStaff]
    serializer_class = UserModerationSerializer

    @extend_schema(
        request=UserModerationSerializer, responses=AdminActionResultSerializer
    )
    def post(self, request, *args, **kwargs):
        from apps.users.models import User

        user = get_object_or_404(User, pk=self.kwargs['pk'])
        ser = UserModerationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        action = ser.validated_data['action']
        reason = ser.validated_data.get('reason', '')
        if action == 'suspend':
            user.is_active = False
        else:
            user.is_active = True
        user.save(update_fields=['is_active', 'last_login'])
        if reason:
            services.create_report(
                reporter=request.user,
                target_type='user',
                target_id=user.id,
                reason='admin_action',
                description=f'{action}: {reason}',
            )
        return Response({'detail': f'User {action}d.'})


class ListingModerationsView(generics.GenericAPIView):
    """Staff list listings requiring or needing moderation review."""

    permission_classes = [IsStaff]
    serializer_class = ListingSerializer

    def get(self, request, *args, **kwargs):
        qs = Listing.objects.select_related('provider__user', 'category')
        status_query = request.query_params.get('status', '').strip()
        if status_query:
            qs = qs.filter(moderation_status=status_query)
        page = self.paginate_queryset(qs)
        serializer = ListingSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class ListingModerationView(generics.GenericAPIView):
    """Staff approve, reject, suspend or remove a single listing."""

    permission_classes = [IsStaff]
    serializer_class = ListingModerationSerializer

    @extend_schema(request=ListingModerationSerializer, responses=ListingSerializer)
    def post(self, request, *args, **kwargs):
        listing = get_object_or_404(Listing, pk=self.kwargs['pk'])
        ser = ListingModerationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        action = ser.validated_data['action']
        note = ser.validated_data.get('note', '')

        transitions = {
            'approve': ('published', True, False),
            'reject': ('rejected', False, False),
            'suspend': ('suspended', False, True),
            'remove': ('archived', False, True),
        }
        moderation_status, is_active, is_archived = transitions[action]
        listing.moderation_status = moderation_status
        listing.is_active = is_active
        listing.is_archived = is_archived
        listing.save(
            update_fields=[
                'moderation_status',
                'is_active',
                'is_archived',
                'updated_at',
            ]
        )

        from apps.notifications.services import notify

        notify(
            recipient=listing.provider.user,
            actor=request.user,
            verb=f'listing_{action}',
            target_type='listing',
            target_id=listing.id,
            data={'title': listing.title, 'note': note},
        )
        return Response(ListingSerializer(listing).data)
