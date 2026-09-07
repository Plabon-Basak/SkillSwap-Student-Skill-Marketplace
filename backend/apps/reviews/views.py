"""API views for ratings and reviews."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.orders.models import Order
from apps.profiles.models import Profile
from apps.reviews import services
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewCreateSerializer, ReviewSerializer
from apps.users.permissions import IsEmailVerified


class ReviewCreateView(generics.GenericAPIView):
    """The buyer writes a review for a completed order they purchased."""

    throttle_scope = 'review_create'
    permission_classes = [IsEmailVerified]
    serializer_class = ReviewCreateSerializer

    @extend_schema(request=ReviewCreateSerializer, responses=ReviewSerializer)
    def post(self, request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if profile is None:
            return Response(
                {'detail': 'Create a profile before writing a review.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = ReviewCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = get_object_or_404(Order, id=ser.validated_data['order'])
        if order.buyer.user_id != request.user.id:
            return Response(
                {'detail': 'Only the order buyer may write a review.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            review = services.create_review(
                order=order,
                reviewer=profile,
                rating=ser.validated_data['rating'],
                comment=ser.validated_data.get('comment', ''),
            )
        except Exception as exc:
            return Response(
                {'detail': str(exc.detail[0])}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class ProfileReviewsView(generics.ListAPIView):
    """Public list of reviews a profile has received, addressed by username."""

    permission_classes = [AllowAny]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        profile = get_object_or_404(
            Profile.objects.select_related('user'), user__username=username
        )
        return (
            Review.objects.filter(reviewee=profile)
            .select_related('reviewer__user')
            .order_by('-created_at')
        )
