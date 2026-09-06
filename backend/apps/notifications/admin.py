"""Admin registrations for notifications."""

from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipient',
        'verb',
        'is_read',
        'target_type',
        'created_at',
    )
    list_filter = ('is_read', 'verb', 'created_at')
    search_fields = ('recipient__email', 'verb')
    readonly_fields = (
        'recipient',
        'actor',
        'verb',
        'target_type',
        'target_id',
        'data',
        'created_at',
    )

    def has_add_permission(self, request):
        return False
