"""API views for the marketplace: listings, categories and applications."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.listings.models import Application, Category, Listing
from apps.listings.permissions import IsProviderOrStaff
from apps.listings.serializers import (
    ApplicationSerializer,
    ApplicationWriteSerializer,
    CategorySerializer,
    ListingSerializer,
    ListingWriteSerializer,
)
from apps.listings.services import (
    accept_application,
    apply_to_listing,
    reject_application,
    withdraw_application,
)
from apps.users.permissions import IsEmailVerified


def _current_profile(user):
    return getattr(user, 'profile', None)


class ListingListCreateView(generics.GenericAPIView):
    """Browse the public market, or create a listing as a provider."""

    permission_classes = [IsEmailVerified]
    serializer_class = ListingSerializer
    throttle_scope = 'listing_create'

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsEmailVerified()]

    def get_queryset(self):
        params = self.request.query_params
        qs = Listing.objects.filter(is_active=True, is_archived=False).select_related(
            'provider__user'
        )

        query = params.get('q', '').strip()
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(skills__name__icontains=query)
                | Q(category__name__icontains=query)
            )

        category = params.get('category', '').strip()
        if category:
            qs = qs.filter(category__slug=category)

        skill = params.get('skill', '').strip()
        if skill:
            qs = qs.filter(skills__slug=skill)

        min_price = params.get('min_price')
        max_price = params.get('max_price')
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        remote = params.get('remote')
        if remote in ('true', 'false'):
            qs = qs.filter(is_remote=remote == 'true')

        location = params.get('location', '').strip()
        if location:
            qs = qs.filter(location__icontains=location)

        provider = params.get('provider', '').strip()
        if provider:
            qs = qs.filter(provider__user__username=provider)

        sort = params.get('sort', 'newest')
        if sort == 'price_asc':
            qs = qs.order_by('price', '-created_at')
        elif sort == 'price_desc':
            qs = qs.order_by('-price', '-created_at')
        else:
            qs = qs.order_by('-created_at')

        return qs.prefetch_related('skills').select_related('category')

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        serializer = ListingSerializer(
            page or qs, many=True, context=self.get_serializer_context()
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        profile = _current_profile(request.user)
        if profile is None:
            return Response(
                {'detail': 'Create a profile before listing a service.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ListingWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = serializer.create_listing(profile)
        out = ListingSerializer(listing, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class MyListingsView(generics.ListAPIView):
    """The provider's own listings, including inactive and archived."""

    permission_classes = [IsEmailVerified]
    serializer_class = ListingSerializer

    def get_queryset(self):
        profile = _current_profile(self.request.user)
        if profile is None:
            return Listing.objects.none()
        return (
            Listing.objects.filter(provider=profile)
            .select_related('provider__user', 'category')
            .prefetch_related('skills')
        )


class ListingDetailView(generics.GenericAPIView):
    """Full listing detail; providers may edit or retire their listings."""

    permission_classes = [IsProviderOrStaff]
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    serializer_class = ListingSerializer
    throttle_scope = 'listing_create'

    def get_queryset(self):
        qs = Listing.objects.select_related(
            'provider__user', 'category'
        ).prefetch_related('skills')
        if not self.request.user.is_authenticated:
            return qs.filter(is_active=True, is_archived=False)
        if self.request.user.is_staff:
            return qs
        own_profile = _current_profile(self.request.user)
        if own_profile is not None:
            return qs.filter(Q(provider=own_profile) | Q(is_archived=False))
        return qs.filter(is_active=True, is_archived=False)

    def get(self, request, *args, **kwargs):
        listing = self.get_object()
        out = ListingSerializer(listing, context={'request': request})
        return Response(out.data)

    def patch(self, request, *args, **kwargs):
        listing = self.get_object()
        serializer = ListingWriteSerializer(listing, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        listing = serializer.update_listing(listing)
        out = ListingSerializer(listing, context={'request': request})
        return Response(out.data)

    def delete(self, request, *args, **kwargs):
        listing = self.get_object()
        listing.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListView(generics.ListAPIView):
    """Browse marketplace categories for filters and pickers."""

    permission_classes = []
    serializer_class = CategorySerializer
    pagination_class = None

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class ListingApplicationsView(generics.GenericAPIView):
    """Applications to one listing; providers list them, buyers apply."""

    throttle_scope = 'application_create'
    serializer_class = ApplicationSerializer

    def _listing_for_request(self):
        return get_object_or_404(Listing, slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        listing = self._listing_for_request()
        if request.user != listing.provider.user and not request.user.is_staff:
            return Response(
                {'detail': 'Only the listing provider can view applications.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = listing.applications.select_related('applicant__user', 'listing')
        page = self.paginate_queryset(qs)
        serializer = ApplicationSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @extend_schema(request=ApplicationWriteSerializer, responses=ApplicationSerializer)
    def post(self, request, *args, **kwargs):
        profile = _current_profile(request.user)
        if profile is None:
            return Response(
                {'detail': 'Create a profile before applying to a listing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        listing = self._listing_for_request()
        if not listing.is_active or listing.is_archived:
            raise ValidationError('This listing is no longer active.')
        ser = ApplicationWriteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            application = apply_to_listing(
                listing,
                profile,
                message=ser.validated_data.get('message', ''),
                proposed_price=ser.validated_data.get('proposed_price'),
            )
        except ValidationError as exc:
            return Response(
                {'detail': str(exc.detail[0])}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            ApplicationSerializer(application).data, status=status.HTTP_201_CREATED
        )


class MyApplicationsView(generics.ListAPIView):
    """The buyer's own applications across all listings."""

    permission_classes = [IsEmailVerified]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        profile = _current_profile(self.request.user)
        if profile is None:
            return Application.objects.none()
        return Application.objects.filter(applicant=profile).select_related(
            'applicant__user', 'listing'
        )


class ApplicationDetailView(generics.RetrieveUpdateAPIView):
    """Respond to an application: the provider accepts/rejects, the buyer withdraws."""

    permission_classes = [IsEmailVerified]
    serializer_class = ApplicationSerializer
    queryset = Application.objects.select_related('applicant__user', 'listing')

    def patch(self, request, *args, **kwargs):
        application = self.get_object()
        action = request.data.get('action')
        if action not in ('accept', 'reject', 'withdraw'):
            return Response(
                {'action': ["Must be one of 'accept', 'reject', 'withdraw'."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        actor = request.user
        if action == 'withdraw':
            if actor != application.applicant.user and not actor.is_staff:
                return Response(
                    {'detail': 'Only the applicant may withdraw an application.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            try:
                withdraw_application(application)
            except ValidationError as exc:
                return Response({'detail': str(exc.detail[0])}, status=400)
        else:
            if actor != application.listing.provider.user and not actor.is_staff:
                return Response(
                    {
                        'detail': 'Only the listing provider may respond to applications.'
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            try:
                if action == 'accept':
                    accept_application(application)
                else:
                    reject_application(application)
            except ValidationError as exc:
                return Response({'detail': str(exc.detail[0])}, status=400)

        return Response(ApplicationSerializer(application).data)
