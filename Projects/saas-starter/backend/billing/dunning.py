"""
Templates and utilities for subscription dunning (payment failure handling).
Sends notifications when payments fail and subscription is at risk.
"""
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('billing')


class SubscriptionDunningManager:
    """
    Manage subscription payment failure notifications and recovery.
    """

    @staticmethod
    def handle_payment_failed(subscription_id, profile, error_message=None):
        """
        Handle payment failure for a subscription.
        - Update status to 'past_due'
        - Send notification email
        - Log for follow-up
        """
        logger.warning(
            f'Payment failed for subscription {subscription_id} (user {profile.user.id}). '
            f'Error: {error_message}'
        )

        # Mark as past due
        profile.subscription_status = 'past_due'
        profile.save(update_fields=['subscription_status', 'updated_at'])

        # Send payment failure notification
        SubscriptionDunningManager.send_payment_failed_email(profile, error_message)

    @staticmethod
    def send_payment_failed_email(profile, error_message=None):
        """
        Send email notification when payment fails.
        """
        if not settings.EMAIL_HOST_USER:
            logger.warning('Email not configured, skipping payment failed notification')
            return

        try:
            subject = '⚠️ Payment Failed - Update Your Billing Information'
            context = {
                'user': profile.user,
                'subscription_status': profile.subscription_status,
                'next_retry': profile.current_period_end,
                'error_message': error_message,
                'billing_portal_url': f'{settings.SITE_URL}/billing/portal/',
            }

            html_message = render_to_string(
                'email/payment_failed.html',
                context
            )
            text_message = f"""
Your payment for {profile.user.get_full_name()} failed.

Stripe will automatically retry your payment several times before canceling your subscription.

Update your billing information: {context['billing_portal_url']}

If you don't have JavaScript enabled, you can also reply to this email.

Error: {error_message}
            """.strip()

            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile.user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f'Payment failed email sent to {profile.user.email}')

        except Exception as e:
            logger.error(f'Failed to send payment failure email: {e}', exc_info=True)

    @staticmethod
    def send_subscription_canceled_email(profile, reason=None):
        """
        Send email notification when subscription is canceled.
        """
        if not settings.EMAIL_HOST_USER:
            logger.warning('Email not configured, skipping subscription canceled notification')
            return

        try:
            subject = '❌ Your Subscription Has Been Canceled'
            context = {
                'user': profile.user,
                'reason': reason,
                'reactivate_url': f'{settings.SITE_URL}/billing/pricing/',
            }

            html_message = render_to_string(
                'email/subscription_canceled.html',
                context
            )
            text_message = f"""
Your {settings.SITE_NAME} subscription has been canceled.

Reason: {reason or 'Not specified'}

You can reactivate your subscription anytime: {context['reactivate_url']}

We're sad to see you go! If you have feedback, please let us know.
            """.strip()

            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile.user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f'Subscription canceled email sent to {profile.user.email}')

        except Exception as e:
            logger.error(f'Failed to send subscription canceled email: {e}', exc_info=True)

    @staticmethod
    def send_trial_ending_soon_email(profile, days_remaining):
        """
        Send notification when trial period is ending soon.
        """
        if not settings.EMAIL_HOST_USER or days_remaining > 5:
            return

        try:
            subject = f'🔔 Your Trial Ends in {days_remaining} Days'
            context = {
                'user': profile.user,
                'days_remaining': days_remaining,
                'pricing_url': f'{settings.SITE_URL}/billing/pricing/',
            }

            html_message = render_to_string(
                'email/trial_ending_soon.html',
                context
            )
            text_message = f"""
Your {settings.SITE_NAME} trial ends in {days_remaining} days.

To continue using Pro features, subscribe now: {context['pricing_url']}

Questions? We're here to help!
            """.strip()

            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[profile.user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f'Trial ending soon email sent to {profile.user.email}')

        except Exception as e:
            logger.error(f'Failed to send trial ending email: {e}', exc_info=True)
