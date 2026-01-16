"""
Stripe Webhook Handler
======================
Production-grade webhook processing with:
- Cryptographic signature verification
- Idempotency protection (no duplicate processing)
- Atomic database transactions
- Comprehensive error handling
- GDPR compliance (no PII storage)
- Stripe as source of truth for subscription state
"""

import logging
import stripe
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

from users.models import Profile
from billing.models import WebhookEvent
from billing.dunning import SubscriptionDunningManager

logger = logging.getLogger("billing")


class StripeWebhookHandler:
    """
    Handles all Stripe webhook events with production-grade safety.
    
    Key features:
    - Verifies webhook signature using STRIPE_WEBHOOK_SECRET
    - Checks WebhookEvent for idempotency
    - Processes event only once
    - Updates Profile correctly based on subscription status
    - Keeps Stripe as authoritative source of subscription data
    """

    # Events we process
    HANDLED_EVENTS = {
        "checkout.session.completed",
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.payment_failed",
        "invoice.payment_succeeded",
    }

    # Status mapping: Stripe → Profile model
    STATUS_MAPPING = {
        "active": "active",
        "trialing": "trialing",
        "past_due": "past_due",
        "canceled": "canceled",
        "unpaid": "unpaid",
    }

    @staticmethod
    def construct_and_verify_event(
        payload: bytes, sig_header: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verify webhook signature and construct event object.
        
        Args:
            payload: Raw webhook payload
            sig_header: Stripe-Signature header value
            
        Returns:
            Event dict if signature is valid, None otherwise
            
        Raises:
            ValueError: Invalid payload
            stripe.error.SignatureVerificationError: Invalid signature
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise

    @staticmethod
    def is_event_processed(event_id: str) -> bool:
        """Check if event was already processed (idempotency)."""
        try:
            webhook_event = WebhookEvent.objects.get(event_id=event_id)
            return webhook_event.processed
        except WebhookEvent.DoesNotExist:
            return False

    @staticmethod
    def get_or_create_webhook_event(
        event_id: str, event_type: str, event: Dict[str, Any]
    ):
        """
        Get or create webhook event record for idempotency.
        
        Returns:
            (webhook_event, created) tuple
        """
        event_hash = WebhookEvent.hash_event(event)
        webhook_event, created = WebhookEvent.objects.get_or_create(
            event_id=event_id,
            defaults={
                "event_type": event_type,
                "event_hash": event_hash,
            },
        )
        return webhook_event, created

    @classmethod
    def process_event(cls, event: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Process a webhook event.
        
        Args:
            event: Stripe webhook event object
            
        Returns:
            (success: bool, error_message: Optional[str]) tuple
        """
        event_id = event.get("id")
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})

        logger.info(f"Processing webhook event {event_id} ({event_type})")

        # Get or create webhook event record
        webhook_event, created = cls.get_or_create_webhook_event(
            event_id, event_type, event
        )

        # Check idempotency: if already processed, skip
        if webhook_event.processed:
            logger.info(f"Webhook event {event_id} already processed, skipping")
            return True, None

        # Process only if this is a handled event type
        if event_type not in cls.HANDLED_EVENTS:
            logger.warning(f"Unhandled webhook event type: {event_type}")
            webhook_event.mark_processed()
            return True, None

        try:
            with transaction.atomic():
                if event_type == "checkout.session.completed":
                    cls._handle_checkout_completed(data)
                elif event_type in [
                    "customer.subscription.created",
                    "customer.subscription.updated",
                ]:
                    cls._handle_subscription_updated(data)
                elif event_type == "customer.subscription.deleted":
                    cls._handle_subscription_deleted(data)
                elif event_type == "invoice.payment_failed":
                    cls._handle_payment_failed(data)
                elif event_type == "invoice.payment_succeeded":
                    cls._handle_payment_succeeded(data)

                # Mark as processed on success
                webhook_event.mark_processed()
                logger.info(f"Successfully processed webhook {event_id} ({event_type})")
                return True, None

        except ValueError as e:
            error_msg = f"Invalid data in webhook {event_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            webhook_event.mark_processed(error_message=error_msg)
            return False, error_msg

        except stripe.error.StripeError as e:
            error_msg = f"Stripe error processing webhook {event_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Don't mark as processed - let Stripe retry
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error processing webhook {event_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Don't mark as processed - let Stripe retry
            return False, error_msg

    @classmethod
    def _handle_checkout_completed(cls, data: Dict[str, Any]) -> None:
        """
        Handle checkout.session.completed event.
        User purchased subscription from checkout.
        """
        user_id = data.get("metadata", {}).get("user_id")
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")

        if not all([user_id, customer_id, subscription_id]):
            raise ValueError(
                f"Missing required fields: user_id={user_id}, "
                f"customer_id={customer_id}, subscription_id={subscription_id}"
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User {user_id} not found")

        profile = user.profile

        # Fetch subscription details from Stripe (Stripe is source of truth)
        subscription = stripe.Subscription.retrieve(subscription_id)

        # Update profile
        profile.is_subscribed = True
        profile.plan = "pro"
        profile.stripe_customer_id = customer_id
        profile.stripe_subscription_id = subscription_id
        profile.subscription_status = subscription.status
        profile.current_period_start = timezone.datetime.fromtimestamp(
            subscription.current_period_start, tz=timezone.utc
        )
        profile.current_period_end = timezone.datetime.fromtimestamp(
            subscription.current_period_end, tz=timezone.utc
        )
        profile.save()

        logger.info(
            f"User {user_id} subscription activated: {subscription_id} ({subscription.status})"
        )

    @classmethod
    def _handle_subscription_updated(cls, data: Dict[str, Any]) -> None:
        """
        Handle customer.subscription.created or customer.subscription.updated.
        Subscription state changed on Stripe's side.
        """
        sub_id = data.get("id")
        stripe_status = data.get("status")

        if not sub_id or not stripe_status:
            raise ValueError(
                f"Missing required fields: id={sub_id}, status={stripe_status}"
            )

        # Fetch full subscription from Stripe
        subscription = stripe.Subscription.retrieve(sub_id)

        # Determine if subscription is active
        is_subscribed = stripe_status in ["active", "trialing"]
        plan = "pro" if is_subscribed else "free"
        mapped_status = cls.STATUS_MAPPING.get(stripe_status, "inactive")

        # Update all profiles with this subscription
        updated_count = Profile.objects.filter(
            stripe_subscription_id=sub_id
        ).update(
            is_subscribed=is_subscribed,
            subscription_status=mapped_status,
            plan=plan,
            current_period_start=timezone.datetime.fromtimestamp(
                subscription.current_period_start, tz=timezone.utc
            ),
            current_period_end=timezone.datetime.fromtimestamp(
                subscription.current_period_end, tz=timezone.utc
            ),
        )

        if updated_count == 0:
            logger.warning(f"No profile found for subscription {sub_id}")
        else:
            logger.info(
                f"Updated {updated_count} profile(s) for subscription {sub_id}: "
                f"status={stripe_status}, plan={plan}"
            )

    @classmethod
    def _handle_subscription_deleted(cls, data: Dict[str, Any]) -> None:
        """
        Handle customer.subscription.deleted event.
        User canceled subscription on Stripe.
        """
        sub_id = data.get("id")
        if not sub_id:
            raise ValueError("Missing subscription ID in deletion event")

        try:
            profile = Profile.objects.get(stripe_subscription_id=sub_id)
        except Profile.DoesNotExist:
            logger.warning(f"No profile found for deleted subscription {sub_id}")
            return

        # Update subscription status
        profile.subscription_status = "canceled"
        profile.plan = "free"
        profile.is_subscribed = False
        profile.save()

        # Send cancellation email
        reason = (
            data.get("cancellation_details", {}).get("reason", "Not specified")
        )
        SubscriptionDunningManager.send_subscription_canceled_email(
            profile, reason=reason
        )

        logger.info(f"Subscription {sub_id} canceled for user {profile.user.id}")

    @classmethod
    def _handle_payment_failed(cls, data: Dict[str, Any]) -> None:
        """
        Handle invoice.payment_failed event.
        Payment attempt failed. Subscription may become past_due.
        Stripe will retry automatically.
        """
        sub_id = data.get("subscription")
        if not sub_id:
            logger.warning("payment_failed event missing subscription ID")
            return

        try:
            profile = Profile.objects.get(stripe_subscription_id=sub_id)
        except Profile.DoesNotExist:
            logger.warning(f"No profile found for subscription {sub_id}")
            return

        # Get error details
        error_message = (
            data.get("last_payment_error", {}).get("message", "Unknown error")
        )

        # Let dunning manager handle the response
        SubscriptionDunningManager.handle_payment_failed(
            sub_id, profile, error_message
        )

        logger.warning(
            f"Payment failed for subscription {sub_id}: {error_message}"
        )

    @classmethod
    def _handle_payment_succeeded(cls, data: Dict[str, Any]) -> None:
        """
        Handle invoice.payment_succeeded event.
        Payment was successfully processed. Subscription should be active.
        """
        sub_id = data.get("subscription")
        if not sub_id:
            logger.warning("payment_succeeded event missing subscription ID")
            return

        # Fetch subscription from Stripe
        subscription = stripe.Subscription.retrieve(sub_id)

        # Update profile
        updated_count = Profile.objects.filter(
            stripe_subscription_id=sub_id
        ).update(
            is_subscribed=True,
            subscription_status=subscription.status,
            plan="pro",
            current_period_end=timezone.datetime.fromtimestamp(
                subscription.current_period_end, tz=timezone.utc
            ),
        )

        if updated_count == 0:
            logger.warning(f"No profile found for subscription {sub_id}")
        else:
            logger.info(f"Payment succeeded for subscription {sub_id}")
