"""URL routing for orders and payments."""

from django.urls import path

from apps.orders import views

urlpatterns = [
    path('orders/', views.OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path(
        'orders/<int:pk>/checkout/',
        views.OrderCheckoutView.as_view(),
        name='order-checkout',
    ),
    path(
        'orders/<int:pk>/mock-confirm/',
        views.OrderMockConfirmView.as_view(),
        name='order-mock-confirm',
    ),
    path('stripe/webhook/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
]
