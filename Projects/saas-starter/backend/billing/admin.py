from django.contrib import admin
from .models import WebhookEvent


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    """Admin interface for webhook events"""
    list_display = [
        'event_id',
        'event_type',
        'processed',
        'processed_at',
        'created_at',
    ]
    list_filter = [
        'event_type',
        'processed',
        'created_at',
    ]
    search_fields = ['event_id', 'event_type']
    readonly_fields = [
        'event_id',
        'event_type',
        'created_at',
        'updated_at',
        'event_data',
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        # Prevent manual creation - events come from Stripe
        return False
