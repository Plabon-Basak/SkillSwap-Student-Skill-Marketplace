"""Admin registrations for the moderation app."""

from django.contrib import admin

from apps.moderation.models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'reporter',
        'target_type',
        'target_id',
        'reason',
        'status',
        'reviewed_by',
        'created_at',
    )
    list_filter = ('status', 'target_type', 'created_at')
    search_fields = ('reporter__email', 'reporter__username', 'reason', 'description')
    readonly_fields = (
        'reporter',
        'target_type',
        'target_id',
        'reason',
        'description',
        'created_at',
    )
