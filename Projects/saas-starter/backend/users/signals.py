import logging
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Profile

logger = logging.getLogger("users")
stripe.api_key = settings.STRIPE_SECRET_KEY


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create Profile when new User is created.
    Safely handles Stripe customer creation failures.
    Ensures user creation succeeds even if Stripe fails.
    """
    if created:
        try:
            # Step 1: Create profile (atomic, guaranteed to succeed)
            profile, profile_created = Profile.objects.get_or_create(user=instance)

            if not profile_created or profile.stripe_customer_id:
                # Profile already exists or already has Stripe ID
                return

            # Step 2: Create Stripe customer (can fail, but won't block user creation)
            _create_stripe_customer(instance, profile)

        except Exception as e:
            # Catch-all for unexpected errors (shouldn't happen)
            logger.exception(f"Error creating profile for user {instance.username}: {e}")
            # Profile is already created at this point, so we're safe


def _create_stripe_customer(user_instance, profile):
    """
    Create Stripe customer for user.
    Handles failures gracefully - profile exists even if Stripe fails.
    Will be retried on first checkout attempt.
    """
    if not settings.STRIPE_SECRET_KEY:
        logger.warning(f"Stripe not configured, skipping customer creation for {user_instance.username}")
        return

    try:
        customer = stripe.Customer.create(
            email=user_instance.email,
            name=user_instance.get_full_name() or user_instance.username,
            metadata={
                "user_id": str(user_instance.id),
                "username": user_instance.username
            }
        )
        profile.stripe_customer_id = customer.id
        profile.save(update_fields=['stripe_customer_id'])
        logger.info(f"Created Stripe customer {customer.id} for user {user_instance.username}")

    except stripe.error.RateLimitError as e:
        # Rate limit - Stripe's servers are busy, will retry on checkout
        logger.warning(
            f"Rate limited creating Stripe customer for {user_instance.username}, "
            f"will retry on checkout"
        )

    except stripe.error.APIConnectionError as e:
        # Network/connection error - will retry on checkout
        logger.warning(
            f"Connection error creating Stripe customer for {user_instance.username}, "
            f"will retry on checkout"
        )

    except stripe.error.InvalidRequestError as e:
        # Invalid request (e.g., bad email) - needs manual fix
        logger.error(
            f"Invalid request creating Stripe customer for {user_instance.username}: {e}"
        )

    except stripe.error.AuthenticationError as e:
        # Auth error - likely bad API key
        logger.error(
            f"Authentication error creating Stripe customer (bad API key?): {e}"
        )

    except stripe.error.StripeError as e:
        # Other Stripe errors
        logger.error(
            f"Stripe error creating customer for {user_instance.username}: {e}",
            exc_info=True
        )

    except Exception as e:
        # Unexpected non-Stripe errors
        logger.error(
            f"Unexpected error creating Stripe customer for {user_instance.username}: {e}",
            exc_info=True
        )

    # Note: Profile exists at this point regardless of whether Stripe succeeded.
    # The checkout view will attempt to create a customer if stripe_customer_id is missing.
