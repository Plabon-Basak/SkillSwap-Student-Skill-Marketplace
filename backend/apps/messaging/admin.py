"""Admin registrations for messaging."""

from django.contrib import admin

from apps.messaging.models import Message, Thread


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'body', 'is_read', 'created_at')


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'buyer', 'provider', 'last_message_at', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__id', 'buyer__user__email', 'provider__user__email')
    inlines = [MessageInline]
