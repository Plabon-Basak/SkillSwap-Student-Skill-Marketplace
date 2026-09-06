"""API views for orders, checkout and the Stripe webhook."""

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.listings.models import Application
from apps.orders import services
from apps.orders.models import Order
from apps.orders.serializers import OrderCreateSerializer, OrderSerializer
from apps.users.permissions import IsEmailVerified

ACTION_WHITELIST = {'cancel', 'start', 'complete'}


def _current_profile(user):
    return getattr(user, 'profile', None)


def _orders_for_user(request):
    profile = _current_profile(request.user)
    if profile is None:
        return Order.objects.none()
    role = request.query_params.get('role', '')
    if role == 'buyer':
        qs = Order.objects.filter(buyer=profile)
    elif role == 'provider':
        qs = Order.objects.filter(provider=profile)
    else:
        qs = Order.objects.filter(Q(buyer=profile) | Q(provider=profile))
    return qs.select_related('buyer__user', 'provider__user', 'listing', 'application')


class OrderListCreateView(generics.GenericAPIView):
    """List the caller's orders or create one from an accepted application."""

    throttle_scope = 'order_create'
    permission_classes = [IsEmailVerified]

    def get(self, request, *args, **kwargs):
        qs = _orders_for_user(request)
        page = self.paginate_queryset(qs)
        serializer = OrderSerializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        profile = _current_profile(request.user)
        if profile is None:
            return Response(
                {'detail': 'Create a profile before placing an order.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = OrderCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        application = get_object_or_404(
            Application, id=ser.validated_data['application']
        )
        if application.applicant.user != request.user and not request.user.is_staff:
            return Response(
                {
                    'detail': 'Only the applicant of this application may place the order.'
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            order = services.create_order(
                application, profile, note=ser.validated_data.get('note', '')
            )
        except Exception as exc:
            return Response(
                {'detail': str(exc.detail[0])}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.GenericAPIView):
    """View an order, or transition it via an explicit action."""

    permission_classes = [IsEmailVerified]

    def _order(self, request):
        profile = _current_profile(request.user)
        qs = Order.objects.select_related(
            'buyer__user', 'provider__user', 'listing', 'application'
        )
        if not request.user.is_staff and profile is not None:
            qs = qs.filter(Q(buyer=profile) | Q(provider=profile))
        elif not request.user.is_staff:
            qs = qs.none()
        return get_object_or_404(qs, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return Response(OrderSerializer(self._order(request)).data)

    def patch(self, request, *args, **kwargs):
        order = self._order(request)
        action = request.data.get('action')
        if action not in ACTION_WHITELIST:
            return Response(
                {'action': ["Must be one of 'cancel', 'start', 'complete'."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if action == 'cancel':
            if request.user.id not in (order.buyer.user_id, order.provider.user_id):
                return Response(
                    {'detail': 'Only participants may cancel this order.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            try:
                order = services.cancel_order(
                    order, cancelled_by=_current_profile(request.user)
                )
            except Exception as exc:
                return Response(
                    {'detail': str(exc.detail[0])}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if request.user != order.provider.user and not request.user.is_staff:
                return Response(
                    {'detail': 'Only the provider may start or complete this order.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            try:
                order = (
                    services.start_order(order)
                    if action == 'start'
                    else services.complete_order(order)
                )
            except Exception as exc:
                return Response(
                    {'detail': str(exc.detail[0])}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(OrderSerializer(order).data)


class OrderCheckoutView(generics.GenericAPIView):
    """Create the payment session for a pending order."""

    throttle_scope = 'order_checkout'

    def get_queryset(self):
        return Order.objects.select_related(
            'buyer__user', 'provider__user', 'listing', 'application'
        )

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        if order.buyer.user_id != request.user.id:
            return Response(
                {'detail': 'Only the buyer may open checkout for this order.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            session = services.gateway().create_checkout_session(order)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(session)


class OrderMockConfirmView(generics.GenericAPIView):
    """Dev-only helper that marks an order paid in simulation mode."""

    def post(self, request, *args, **kwargs):
        if services.CONFIGURED:
            raise Http404('Real checkout configured; this endpoint is disabled.')
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        order = services.mark_order_paid(order, gateway_charge_id='simulated')
        return Response(OrderSerializer(order).data)


class StripeWebhookView(generics.GenericAPIView):
    """Receives Stripe events; signature is verified when configured."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            services.gateway().handle_webhook(request)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
