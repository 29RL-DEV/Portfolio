from django.db import models
from django.utils import timezone
from django.conf import settings


class WebhookEvent(models.Model):
    """
    Track processed Stripe webhook events for idempotency.
    Prevents duplicate processing of the same event.
    """
    event_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Stripe event ID (evt_xxx)"
    )
    event_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Stripe event type (e.g., checkout.session.completed)"
    )
    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this event has been successfully processed"
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the event was processed"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if processing failed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SHA256 hash of event data for verification (no PII stored)
    event_hash = models.CharField(
        max_length=64,
        default='',
        help_text="SHA256 hash of event data for verification"
    )

    def __str__(self):
        return f"{self.event_type} - {self.event_id} ({'processed' if self.processed else 'pending'})"

    @staticmethod
    def hash_event(event_data):
        """Create SHA256 hash of event for verification"""
        import hashlib
        import json
        try:
            data_str = json.dumps(event_data, sort_keys=True, default=str)
            return hashlib.sha256(data_str.encode()).hexdigest()
        except Exception:
            return ''

    def mark_processed(self, error_message=None):
        """Mark event as processed"""
        self.processed = True
        self.processed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save(update_fields=['processed', 'processed_at', 'error_message', 'updated_at'])

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_id']),
            models.Index(fields=['event_type', 'processed']),
        ]


class Subscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription"
    )
    stripe_customer_id = models.CharField(max_length=255, db_index=True)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=50,
        db_index=True,
        help_text="active, trialing, past_due, canceled, unpaid"
    )
    current_period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_active(self):
        return self.status in ["active", "trialing"]

    def __str__(self):
        return f"{self.user.email} – {self.status}"

    class Meta:
        ordering = ['-created_at']