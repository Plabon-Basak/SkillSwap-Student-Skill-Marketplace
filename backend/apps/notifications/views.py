"""API views for the in-app notification center."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.response import Response

from apps.notifications import services
from apps.notifications.models import Notification
from apps.notifications.serializers import (
    MarkedReadSerializer,
    NotificationSerializer,
    UnreadCountSerializer,
)
from apps.users.permissions import IsEmailVerified


class MyNotificationsView(generics.GenericAPIView):
    permission_classes = [IsEmailVerified]
    serializer_class = NotificationSerializer

    def get(self, request, *args, **kwargs):
        qs = Notification.objects.filter(recipient=request.user)
        if request.query_params.get('unread') == 'true':
            qs = qs.filter(is_read=False)
        page = self.paginate_queryset(qs)
        serializer = NotificationSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class NotificationUnreadCountView(generics.GenericAPIView):
    permission_classes = [IsEmailVerified]

    @extend_schema(responses=UnreadCountSerializer)
    def get(self, request, *args, **kwargs):
        return Response({'count': services.unread_count_for(request.user)})


class NotificationReadView(generics.GenericAPIView):
    permission_classes = [IsEmailVerified]
    serializer_class = NotificationSerializer

    @extend_schema(request=None, responses=NotificationSerializer)
    def post(self, request, *args, **kwargs):
        notification = get_object_or_404(
            Notification, pk=self.kwargs['pk'], recipient=request.user
        )
        services.mark_notification_read(notification)
        return Response(NotificationSerializer(notification).data)


class NotificationReadAllView(generics.GenericAPIView):
    permission_classes = [IsEmailVerified]

    @extend_schema(request=None, responses=MarkedReadSerializer)
    def post(self, request, *args, **kwargs):
        updated = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return Response({'marked_read': updated})
