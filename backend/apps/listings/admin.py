from django.contrib import admin

from apps.listings.models import Application, Category, Listing


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'provider_username',
        'category',
        'price',
        'is_active',
        'is_archived',
        'created_at',
    )
    search_fields = ('title', 'description', 'provider__user__username')
    list_filter = ('is_active', 'is_archived', 'is_remote', 'category')
    filter_horizontal = ('skills',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('listing', 'applicant', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('listing__title', 'applicant__user__username')
