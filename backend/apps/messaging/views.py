"""API views for order conversation threads."""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from apps.messaging import services
from apps.messaging.models import Thread
from apps.messaging.serializers import MessageSerializer, ThreadSerializer
from apps.users.permissions import IsEmailVerified


def _current_profile(user):
    return getattr(user, 'profile', None)


def _thread_for_user(request, thread_pk):
    profile = _current_profile(request.user)
    qs = Thread.objects.select_related('order', 'buyer__user', 'provider__user')
    if not request.user.is_staff:
        if profile is None:
            qs = qs.none()
        qs = qs.filter(buyer=profile) | qs.filter(provider=profile)
    return get_object_or_404(qs, pk=thread_pk)


class MyThreadsView(generics.GenericAPIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, *args, **kwargs):
        profile = _current_profile(request.user)
        if request.user.is_staff:
            qs = Thread.objects.all()
        elif profile is not None:
            qs = Thread.objects.filter(buyer=profile) | Thread.objects.filter(
                provider=profile
            )
        else:
            qs = Thread.objects.none()
        qs = qs.select_related('order', 'buyer__user', 'provider__user')
        page = self.paginate_queryset(qs)
        serializer = ThreadSerializer(page, many=True, context={'profile': profile})
        return self.get_paginated_response(serializer.data)


class ThreadDetailView(generics.GenericAPIView):
    permission_classes = [IsEmailVerified]

    def _thread(self, request):
        return _thread_for_user(request, self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        profile = _current_profile(request.user)
        thread = self._thread(request)
        if not request.user.is_staff:
            services.mark_thread_read(thread, profile)
        return Response(ThreadSerializer(thread, context={'profile': profile}).data)


class ThreadMessageListCreateView(generics.GenericAPIView):
    permission_classes = [IsEmailVerified]
    throttle_scope = 'message_send'

    def _thread(self, request):
        return _thread_for_user(request, self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        thread = self._thread(request)
        messages = thread.messages.select_related('sender__user').all()
        page = self.paginate_queryset(messages)
        serializer = MessageSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        profile = _current_profile(request.user)
        thread = self._thread(request)
        if request.user.is_staff:
            return Response(
                {'detail': 'Staff cannot post in participant threads.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        body = (request.data.get('body') or '').strip()
        if not body:
            return Response(
                {'body': ['This field may not be blank.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        message = services.send_message(thread, profile, body=body)
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


class ThreadUnreadCountView(generics.GenericAPIView):
    permission_classes = [IsEmailVerified]

    def get(self, request, *args, **kwargs):
        profile = _current_profile(request.user)
        threads = Thread.objects.filter(buyer=profile) | Thread.objects.filter(
            provider=profile
        )
        total = sum(services.unread_count_for(t, profile) for t in threads)
        return Response({'count': total})
