"""Admin registrations for reviews."""

from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'reviewer',
        'reviewee',
        'rating',
        'created_at',
    )
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewee__user__email', 'reviewer__user__email', 'comment')
