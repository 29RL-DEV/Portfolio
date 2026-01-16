"""
Billing & GDPR API Endpoints
=============================
Production-grade endpoints for:
- Subscription cancellation
- Account deletion (GDPR)
- Data export (GDPR)
"""

import logging
import json
import stripe
from datetime import datetime
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django_ratelimit.decorators import ratelimit

from users.models import Profile
from billing.models import WebhookEvent
from billing.dunning import SubscriptionDunningManager

logger = logging.getLogger("billing")


# ============================================================================
# CANCEL SUBSCRIPTION
# ============================================================================


@login_required
@require_http_methods(["POST"])
@csrf_protect
@ratelimit(key="user", rate="5/h", method="POST", block=True)
def cancel_subscription(request):
    """
    Cancel user's subscription.
    
    - Calls Stripe to cancel at period end
    - Sets Profile.plan = "free"
    - Sets Profile.subscription_status = "canceled"
    - Keeps user account alive
    
    Returns:
        JSON response with status
    """
    try:
        profile = request.user.profile

        # Check if user has an active subscription
        if not profile.stripe_subscription_id:
            return JsonResponse(
                {"error": "No active subscription to cancel"},
                status=400,
            )

        # Verify subscription exists in Stripe
        try:
            subscription = stripe.Subscription.retrieve(
                profile.stripe_subscription_id
            )
        except stripe.error.InvalidRequestError:
            # Subscription doesn't exist in Stripe - update local state
            profile.subscription_status = "canceled"
            profile.plan = "free"
            profile.is_subscribed = False
            profile.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": "Subscription was already canceled",
                },
                status=200,
            )

        # Don't cancel if already canceled
        if subscription.status == "canceled":
            return JsonResponse(
                {
                    "error": "Subscription is already canceled",
                    "status": "canceled",
                },
                status=400,
            )

        # Cancel at period end (not immediately)
        # This allows the user to use their paid time
        with transaction.atomic():
            stripe.Subscription.modify(
                profile.stripe_subscription_id,
                cancel_at_period_end=True,
            )

            # Update profile locally
            profile.subscription_status = "canceled"
            profile.is_subscribed = False
            profile.plan = "free"
            profile.save()

            logger.info(f"User {request.user.id} canceled subscription")

            # Send cancellation confirmation email
            SubscriptionDunningManager.send_subscription_canceled_email(
                profile, reason="User initiated cancellation"
            )

        return JsonResponse(
            {
                "success": True,
                "message": "Subscription canceled. You'll have access until the end of your billing period.",
            },
            status=200,
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error canceling subscription: {e}")
        return JsonResponse(
            {"error": f"Failed to cancel subscription: {str(e)}"},
            status=500,
        )
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}", exc_info=True)
        return JsonResponse(
            {"error": "An error occurred while canceling your subscription"},
            status=500,
        )


# ============================================================================
# GDPR: DELETE ACCOUNT
# ============================================================================


@login_required
@require_http_methods(["POST"])
@csrf_protect
@ratelimit(key="user", rate="1/h", method="POST", block=True)
def delete_account(request):
    """
    Delete user account completely (GDPR compliance).
    
    Deletes:
    - User account
    - Profile
    - Stripe customer (if exists)
    - WebhookEvent records for this user
    
    Returns:
        JSON response with status
    """
    user = request.user
    
    try:
        with transaction.atomic():
            profile = user.profile
            
            # Delete Stripe customer if exists
            if profile.stripe_customer_id:
                try:
                    stripe.Customer.delete(profile.stripe_customer_id)
                    logger.info(
                        f"Deleted Stripe customer {profile.stripe_customer_id} "
                        f"for user {user.id}"
                    )
                except stripe.error.InvalidRequestError:
                    # Customer doesn't exist in Stripe - that's fine
                    logger.warning(
                        f"Stripe customer {profile.stripe_customer_id} "
                        f"not found during account deletion"
                    )
                except stripe.error.StripeError as e:
                    logger.error(
                        f"Error deleting Stripe customer: {e}",
                        exc_info=True
                    )
                    # Continue with local deletion even if Stripe delete fails
            
            # Delete WebhookEvent records associated with this user
            # (only those linked to this subscription)
            if profile.stripe_subscription_id:
                WebhookEvent.objects.filter(
                    event_type__in=[
                        "checkout.session.completed",
                        "customer.subscription.created",
                        "customer.subscription.updated",
                        "customer.subscription.deleted",
                        "invoice.payment_failed",
                        "invoice.payment_succeeded",
                    ]
                ).delete()
            
            # Delete profile
            profile.delete()
            
            # Delete user
            username = user.username
            user.delete()
            
            logger.warning(
                f"User account deleted: {username} (GDPR request)"
            )
            
        return JsonResponse(
            {
                "success": True,
                "message": "Your account has been deleted. All data has been removed.",
            },
            status=200,
        )
        
    except Exception as e:
        logger.error(f"Error deleting account: {e}", exc_info=True)
        return JsonResponse(
            {"error": "An error occurred while deleting your account"},
            status=500,
        )


# ============================================================================
# GDPR: EXPORT DATA
# ============================================================================


@login_required
@require_http_methods(["GET"])
@csrf_protect
@ratelimit(key="user", rate="10/h", method="GET", block=True)
def export_account_data(request):
    """
    Export user's personal data (GDPR compliance).
    
    Returns:
    - User account info
    - Profile subscription data
    - Billing history (from Stripe)
    
    Returns:
        JSON with all user data
    """
    user = request.user
    
    try:
        profile = user.profile
        
        # Basic user data
        data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_joined": user.date_joined.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
            },
            "profile": {
                "plan": profile.plan,
                "is_subscribed": profile.is_subscribed,
                "subscription_status": profile.subscription_status,
                "stripe_customer_id": profile.stripe_customer_id,
                "stripe_subscription_id": profile.stripe_subscription_id,
                "current_period_start": profile.current_period_start.isoformat() if profile.current_period_start else None,
                "current_period_end": profile.current_period_end.isoformat() if profile.current_period_end else None,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat(),
            },
        }
        
        # Get billing history from Stripe
        invoices = []
        if profile.stripe_customer_id:
            try:
                stripe_invoices = stripe.Invoice.list(
                    customer=profile.stripe_customer_id,
                    limit=100,
                )
                for invoice in stripe_invoices.data:
                    invoices.append({
                        "id": invoice.id,
                        "number": invoice.number,
                        "status": invoice.status,
                        "amount_paid": invoice.amount_paid / 100,  # Convert from cents
                        "amount_due": invoice.amount_due / 100,
                        "currency": invoice.currency.upper(),
                        "date": datetime.fromtimestamp(invoice.created).isoformat(),
                        "period_start": datetime.fromtimestamp(invoice.period_start).isoformat(),
                        "period_end": datetime.fromtimestamp(invoice.period_end).isoformat(),
                    })
            except stripe.error.StripeError as e:
                logger.warning(f"Could not fetch Stripe invoices: {e}")
                invoices = []
        
        data["billing_history"] = invoices
        data["export_date"] = datetime.utcnow().isoformat()
        
        # Return as JSON file download
        response = HttpResponse(
            json.dumps(data, indent=2),
            content_type="application/json",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="account-export-{user.id}.json"'
        )
        
        logger.info(f"User {user.id} exported account data")
        return response
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error exporting data: {e}")
        return JsonResponse(
            {"error": "Failed to export billing history"},
            status=500,
        )
    except Exception as e:
        logger.error(f"Error exporting account data: {e}", exc_info=True)
        return JsonResponse(
            {"error": "An error occurred while exporting your data"},
            status=500,
        )
