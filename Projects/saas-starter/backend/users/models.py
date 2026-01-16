from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger('users')


class Profile(models.Model):
    SUBSCRIPTION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
        ('canceled', 'Canceled'),
        ('inactive', 'Inactive'),
        ('trialing', 'Trialing'),  # Added this as it's commonly used by Stripe
    ]

    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
    ]

    # Valid state transitions for subscription lifecycle
    VALID_TRANSITIONS = {
        'inactive': ['trialing', 'active'],
        'trialing': ['active', 'canceled'],
        'active': ['past_due', 'canceled'],
        'past_due': ['active', 'canceled', 'unpaid'],
        'unpaid': ['active', 'canceled'],
        'canceled': ['active'],  # Allow reactivation
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Subscription Status
    is_subscribed = models.BooleanField(default=False, db_index=True)
    subscription_status = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default='inactive',
        db_index=True,
        help_text="Current subscription status"
    )
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='free',
        db_index=True,
        help_text="Current plan: free or pro"
    )

    # Stripe IDs
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text="Stripe Customer ID (cus_xxx)"
    )

    stripe_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text="Stripe Subscription ID (sub_xxx)"
    )

    # Billing Dates
    current_period_start = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Billing period start date"
    )
    current_period_end = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Billing period end date / next renewal date"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stripe_customer_id']),
            models.Index(fields=['stripe_subscription_id']),
            models.Index(fields=['is_subscribed']),
            models.Index(fields=['plan']),
            models.Index(fields=['subscription_status', 'is_subscribed']),
        ]

    def __str__(self):
        return f"{self.user.username} – {self.get_plan_display()} ({self.get_subscription_status_display()})"

    def is_past_due(self):
        """Check if subscription is past due"""
        return self.subscription_status == 'past_due'

    def is_active(self):
        """
        Stripe-authoritative subscription status
        """
        if not self.stripe_subscription_id:
            return False

        # Consider both active and trialing statuses as active
        if self.subscription_status not in ["active", "trialing"]:
            return False

        if self.current_period_end and self.current_period_end < timezone.now():
            return False

        return True

    def days_until_renewal(self):
        """Return days until next renewal, or None if not subscribed"""
        if not self.current_period_end:
            return None
        
        today = timezone.now().date()
        renewal_date = self.current_period_end.date()
        
        # Handle cases where renewal is in the past
        if renewal_date < today:
            return 0
        
        return (renewal_date - today).days

    @property
    def has_active_subscription(self):
        """Property for easier template access"""
        return self.is_active()

    def set_subscription_status(self, new_status):
        """
        Safely transition subscription status.
        Only allows valid state transitions per subscription lifecycle.
        
        Args:
            new_status: Target subscription status
            
        Raises:
            ValidationError: If transition is invalid
        """
        if new_status not in [choice[0] for choice in self.SUBSCRIPTION_STATUS_CHOICES]:
            raise ValidationError(f"Invalid status: {new_status}")

        current = self.subscription_status or 'inactive'
        allowed_transitions = self.VALID_TRANSITIONS.get(current, [])

        if new_status not in allowed_transitions:
            raise ValidationError(
                f"Cannot transition from '{current}' to '{new_status}'. "
                f"Allowed: {', '.join(allowed_transitions)}"
            )

        # Safe atomic update
        self.subscription_status = new_status
        self.is_subscribed = new_status in ['active', 'trialing', 'past_due']
        self.save(update_fields=['subscription_status', 'is_subscribed', 'updated_at'])

        logger.info(f"User {self.user.id} subscription: {current} -> {new_status}")

    def update_subscription_status(self, stripe_status):
        """
        Update subscription status based on Stripe webhook data.
        Stripe is the authoritative source for subscription status.
        
        Args:
            stripe_status: Status from Stripe API/webhooks
        """
        status_mapping = {
            'active': 'active',
            'trialing': 'trialing',
            'past_due': 'past_due',
            'canceled': 'canceled',
            'unpaid': 'unpaid',
        }

        new_status = status_mapping.get(stripe_status, 'inactive')

        try:
            # Try safe transition first
            self.set_subscription_status(new_status)
        except ValidationError as e:
            # If transition fails, force update (Stripe is authoritative)
            logger.warning(
                f"Invalid transition for user {self.user.id}: {current} -> {new_status}. "
                f"Forcing update (Stripe is authoritative). Error: {e}"
            )
            self.subscription_status = new_status
            self.is_subscribed = new_status in ['active', 'trialing', 'past_due']
            self.save(update_fields=['subscription_status', 'is_subscribed', 'updated_at'])