import os
import logging
import stripe
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from users.models import Profile
from billing.dunning import SubscriptionDunningManager

logger = logging.getLogger("billing")

# Only set Stripe API key if it's configured
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


# ===============================
# PRICING PAGE
# ===============================
def pricing_page(request):
    context = {
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, "pricing.html", context)


# ===============================
# CREATE CHECKOUT SESSION
# ===============================
@login_required
def create_checkout_session(request):
    # Check if Stripe is properly configured
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PRICE_ID:
        messages.error(
            request,
            "Stripe nu este configurat corect. Contactează administratorul. "
            "(STRIPE_SECRET_KEY și STRIPE_PRICE_ID sunt necesare)",
        )
        return redirect("/billing/pricing/")

    # Optimize: use select_related to avoid N+1 queries
    user = User.objects.select_related('profile').get(id=request.user.id)
    profile = user.profile

    # Check if customer ID needs to be reset (test vs live mode mismatch)
    if profile.stripe_customer_id:
        if profile.stripe_customer_id.startswith(
            "cus_"
        ) and settings.STRIPE_SECRET_KEY.startswith("sk_live_"):
            # Customer ID is from test mode but we're using live keys - reset it
            logger.warning(
                f"Resetting test mode customer ID {profile.stripe_customer_id} for user {request.user.id}"
            )
            profile.stripe_customer_id = None
            profile.stripe_subscription_id = None
            profile.save()

    if not profile.stripe_customer_id:
        customer = stripe.Customer.create(
            email=request.user.email,
            name=request.user.get_full_name() or request.user.username,
            metadata={"user_id": str(request.user.id)},
        )
        profile.stripe_customer_id = customer.id
        profile.save()

    base_url = os.getenv("BASE_URL", f"{request.scheme}://{request.get_host()}")

    try:
        session = stripe.checkout.Session.create(
            customer=profile.stripe_customer_id,
            mode="subscription",
            line_items=[
                {
                    "price": settings.STRIPE_PRICE_ID,
                    "quantity": 1,
                }
            ],
            success_url=f"{base_url}/billing/success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/billing/cancel/",
            client_reference_id=str(request.user.id),
            metadata={"user_id": str(request.user.id)},
        )
        return redirect(session.url)
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Stripe error: {e}")
        if "live mode" in str(e) and "test mode" in str(e):
            messages.error(
                request,
                "Eroare configurare Stripe: Price ID-ul este din modul live, dar cheile sunt din modul test. "
                "Folosește un Price ID din modul test sau schimbă cheile la live mode.",
            )
        else:
            messages.error(request, f"Eroare Stripe: {str(e)}")
        return redirect("/billing/pricing/")
    except Exception as e:
        logger.error(f"Unexpected error creating checkout session: {e}")
        messages.error(request, "A apărut o eroare. Te rugăm să încerci din nou.")
        return redirect("/billing/pricing/")


# ===============================
# SUCCESS (Stripe only redirects here)
# ===============================
@login_required
def billing_success(request):
    """Mark subscription as active after successful checkout"""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string

    profile = request.user.profile

    # Check subscription status with Stripe
    if profile.stripe_customer_id:
        try:
            subscriptions = stripe.Subscription.list(
                customer=profile.stripe_customer_id, status="active", limit=1
            )
            if subscriptions.data:
                # Active subscription found - mark as pro
                subscription = subscriptions.data[0]
                profile.is_pro = True
                profile.stripe_subscription_id = subscription.id
                profile.save()

                # Send confirmation email
                if settings.EMAIL_HOST_USER:
                    try:
                        send_mail(
                            subject="🎉 Subscription Confirmed - Welcome to Pro!",
                            message=f"Welcome to Pro plan, {request.user.first_name or request.user.username}!\n\n"
                            f"Your subscription has been activated.\n"
                            f"Next billing date: {subscription.current_period_end}\n\n"
                            f"Thank you for subscribing!",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[request.user.email],
                            fail_silently=True,
                        )
                        logger.info(
                            f"Subscription confirmation email sent to {request.user.email}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to send subscription email: {e}")

                messages.success(
                    request,
                    "✅ Subscription activated! Welcome to Pro plan. Confirmation email sent.",
                )
            else:
                messages.info(
                    request, "Subscription pending. Check your email for confirmation."
                )
        except Exception as e:
            logger.error(f"Error checking subscription status: {e}")
            messages.info(request, "Verifying your subscription...")

    return redirect("/billing/status/")


# ===============================
# CANCEL
# ===============================
@login_required
def billing_cancel(request):
    return render(request, "payment_cancel.html")


# ===============================
# BILLING STATUS PAGE
# ===============================
@login_required
def billing_status(request):
    profile = request.user.profile
    context = {"profile": profile, "subscription": None, "invoice_history": []}

    if profile.stripe_subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(profile.stripe_subscription_id)
            context["subscription"] = subscription

            # Get invoice history
            invoices = stripe.Invoice.list(
                customer=profile.stripe_customer_id, limit=10
            )
            context["invoice_history"] = invoices.data
        except Exception as e:
            logger.error(f"Error fetching subscription: {e}")

    return render(request, "billing_status.html", context)


# ===============================
# BILLING DASHBOARD
# ===============================
@login_required
def billing_dashboard(request):
    profile = request.user.profile
    context = {
        "profile": profile,
        "has_subscription": profile.is_subscribed,
        "subscription_status": profile.get_subscription_status_display(),
    }
    return render(request, "billing.html", context)


# ===============================
# CUSTOMER PORTAL (Cancel, update card, invoices)
# ===============================
@login_required
def customer_portal(request):
    profile = request.user.profile

    if not profile.stripe_customer_id:
        return redirect("/billing/")

    # Get base URL from environment or construct from request
    base_url = os.getenv("BASE_URL", f"{request.scheme}://{request.get_host()}")

    session = stripe.billing_portal.Session.create(
        customer=profile.stripe_customer_id, return_url=f"{base_url}/billing/"
    )

    return redirect(session.url)


# ===============================
# STRIPE WEBHOOK (SINGLE SOURCE OF TRUTH)
# ===============================
from django_ratelimit.decorators import ratelimit
from django.db import transaction
from billing.models import WebhookEvent
from billing.webhooks import StripeWebhookHandler
from config.webhook_ratelimit import webhook_rate_limit


@csrf_exempt
@webhook_rate_limit(max_per_minute=100)
def stripe_webhook(request):
    """
    Handle Stripe webhook events using production-grade handler.
    - Signature verification
    - Idempotency protection
    - Database transactions
    - Comprehensive error handling
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    # Verify webhook signature
    if not sig_header:
        logger.warning("Stripe webhook received without signature header")
        return HttpResponse(status=403)

    # Verify signature and construct event
    try:
        event = StripeWebhookHandler.construct_and_verify_event(payload, sig_header)
        if not event:
            return HttpResponse(status=400)
    except ValueError:
        return HttpResponse(status=400)  # Bad request - don't retry
    except Exception as e:
        logger.error(f"Webhook verification error: {e}")
        return HttpResponse(status=503)  # Retry

    # Process event using handler
    success, error_msg = StripeWebhookHandler.process_event(event)
    
    if success:
        return HttpResponse(status=200)
    else:
        # If error, return appropriate status code
        if isinstance(error_msg, str) and "Invalid data" in error_msg:
            return HttpResponse(status=400)
        else:
            return HttpResponse(status=500)
