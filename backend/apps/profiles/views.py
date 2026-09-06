"""API views for student profiles."""

from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.profiles.models import Profile, Skill
from apps.profiles.serializers import (
    ProfilePublicSerializer,
    ProfileSelfSerializer,
    ProfileWriteSerializer,
    SkillSerializer,
)
from apps.profiles.services import search_profiles
from apps.users.permissions import IsEmailVerified


def _annotated(qs):
    return qs.annotate(
        rating_average=Avg('reviews_received__rating'),
        rating_count=Count('reviews_received'),
    )


class MyProfileView(generics.GenericAPIView):
    """Read, create and update the authenticated user's own profile."""

    permission_classes = [IsAuthenticated, IsEmailVerified]

    def _profile(self):
        return get_object_or_404(Profile, user=self.request.user)

    def _ensure_staff_only(self):
        # Non-staff users may not self-grant the verified badge.
        if (
            'is_verified_student' in self.request.data
            and not self.request.user.is_staff
        ):
            return False
        return True

    def get(self, request, *args, **kwargs):
        profile = self._profile()
        return Response(ProfileSelfSerializer(profile).data)

    def post(self, request, *args, **kwargs):
        if Profile.objects.filter(user=request.user).exists():
            return Response(
                {'detail': 'A profile already exists; update it with PATCH.'},
                status=status.HTTP_409_CONFLICT,
            )
        if not self._ensure_staff_only():
            return Response(
                {'is_verified_student': ['Only staff may set this field.']},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ProfileWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.create_profile(request.user)
        return Response(
            ProfileSelfSerializer(profile).data, status=status.HTTP_201_CREATED
        )

    def patch(self, request, *args, **kwargs):
        profile = self._profile()
        if not self._ensure_staff_only():
            return Response(
                {'is_verified_student': ['Only staff may set this field.']},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ProfileWriteSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = serializer.update_profile(profile)
        return Response(ProfileSelfSerializer(profile).data)


class ProfileListView(generics.ListAPIView):
    """Public, searchable listing of student profiles."""

    permission_classes = [AllowAny]
    serializer_class = ProfilePublicSerializer

    def get_queryset(self):
        params = self.request.query_params
        qs = search_profiles(
            query=params.get('q', ''),
            university=params.get('university', ''),
            skill=params.get('skill', ''),
        )
        if params.get('verified') == 'true':
            qs = qs.filter(is_verified_student=True)
        return _annotated(qs)


class ProfileDetailView(generics.RetrieveAPIView):
    """A single public profile, addressed by username."""

    permission_classes = [AllowAny]
    serializer_class = ProfilePublicSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'

    def get_queryset(self):
        return _annotated(
            Profile.objects.filter(is_searchable=True)
            .select_related('user')
            .prefetch_related('skills')
        )


class SkillListView(generics.ListAPIView):
    """Browse skills; used for search suggestions and tag pickers."""

    permission_classes = [AllowAny]
    serializer_class = SkillSerializer
    pagination_class = None

    def get_queryset(self):
        qs = Skill.objects.all()
        query = self.request.query_params.get('search', '').strip()
        if query:
            qs = qs.filter(name__icontains=query)
        return qs[:100]
