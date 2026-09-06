"""Admin registrations for orders and payments."""

from django.contrib import admin

from apps.orders.models import Order, Payment


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('gateway', 'gateway_session_id', 'gateway_charge_id')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'status',
        'buyer',
        'provider',
        'listing',
        'price',
        'currency',
        'created_at',
    )
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('buyer__user__email', 'provider__user__email')
    readonly_fields = (
        'application',
        'buyer',
        'provider',
        'listing',
        'price',
        'currency',
        'paid_at',
        'started_at',
        'completed_at',
        'cancelled_at',
        'created_at',
        'updated_at',
    )
    inlines = [PaymentInline]

    def has_add_permission(self, request):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'amount',
        'currency',
        'status',
        'gateway',
        'created_at',
    )
    list_filter = ('status', 'gateway', 'currency')
    readonly_fields = (
        'order',
        'amount',
        'currency',
        'gateway',
        'gateway_session_id',
        'gateway_charge_id',
        'created_at',
        'updated_at',
    )

    def has_add_permission(self, request):
        return False
