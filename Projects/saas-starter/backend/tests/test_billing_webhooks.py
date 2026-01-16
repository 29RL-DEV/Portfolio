import pytest
import json
from unittest.mock import patch, MagicMock
import stripe
from django.test import Client
from django.utils import timezone
from billing.models import WebhookEvent
from users.models import Profile


@pytest.mark.django_db
class TestStripeWebhooks:
    """Test Stripe webhook handling"""

    def test_webhook_signature_verification(self, stripe_webhook_payload):
        """Webhook must verify Stripe signature"""
        client = Client()

        # Missing signature header should be rejected
        response = client.post(
            '/billing/webhook/',
            data=json.dumps(stripe_webhook_payload),
            content_type='application/json'
        )
        assert response.status_code in [400, 403]

    @patch('stripe.Webhook.construct_event')
    def test_webhook_idempotency(self, mock_construct, db, user, stripe_webhook_payload):
        """Same webhook should only process once"""
        mock_construct.return_value = stripe_webhook_payload

        client = Client()

        # Prepare user with Stripe customer
        profile = user.profile
        profile.stripe_customer_id = 'cus_test123'
        profile.save()

        # First request
        response1 = client.post(
            '/billing/webhook/',
            data=json.dumps(stripe_webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_sig'
        )
        assert response1.status_code == 200

        # Verify webhook logged
        assert WebhookEvent.objects.filter(
            event_id='evt_test123'
        ).exists()

        initial_count = WebhookEvent.objects.filter(
            event_id='evt_test123'
        ).count()

        # Second identical request
        response2 = client.post(
            '/billing/webhook/',
            data=json.dumps(stripe_webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_sig'
        )
        assert response2.status_code == 200

        # Should still be one webhook event (not duplicate)
        final_count = WebhookEvent.objects.filter(
            event_id='evt_test123'
        ).count()
        assert initial_count == final_count

    @patch('stripe.Webhook.construct_event')
    def test_checkout_completed_creates_subscription(self, mock_construct, db, user):
        """checkout.session.completed should activate subscription"""
        payload = {
            'id': 'evt_checkout_123',
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_123',
                    'customer': 'cus_123',
                    'subscription': 'sub_123',
                    'metadata': {'user_id': str(user.id)}
                }
            }
        }

        mock_construct.return_value = payload

        with patch('stripe.Subscription.retrieve') as mock_retrieve:
            mock_retrieve.return_value = MagicMock(
                status='active',
                current_period_start=1000000,
                current_period_end=2000000,
                id='sub_123'
            )

            # Prepare user
            profile = user.profile
            profile.stripe_customer_id = 'cus_123'
            profile.save()

            client = Client()
            response = client.post(
                '/billing/webhook/',
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test_sig'
            )

            assert response.status_code == 200

            # Verify subscription activated
            user.profile.refresh_from_db()
            assert user.profile.is_subscribed == True
            assert user.profile.stripe_subscription_id == 'sub_123'

    @patch('stripe.Webhook.construct_event')
    def test_payment_failed_updates_status(self, mock_construct, db, profile_with_stripe):
        """invoice.payment_failed should update status"""
        payload = {
            'id': 'evt_payment_failed_123',
            'type': 'invoice.payment_failed',
            'data': {
                'object': {
                    'subscription': profile_with_stripe.stripe_subscription_id
                }
            }
        }

        mock_construct.return_value = payload

        client = Client()
        response = client.post(
            '/billing/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_sig'
        )

        assert response.status_code == 200

        profile_with_stripe.refresh_from_db()
        # Should be updated to unpaid or past_due
        assert profile_with_stripe.subscription_status in ['unpaid', 'past_due']

    @patch('stripe.Webhook.construct_event')
    def test_subscription_deleted(self, mock_construct, db, profile_with_stripe):
        """customer.subscription.deleted should cancel subscription"""
        payload = {
            'id': 'evt_deleted_123',
            'type': 'customer.subscription.deleted',
            'data': {
                'object': {
                    'id': profile_with_stripe.stripe_subscription_id,
                    'status': 'canceled'
                }
            }
        }

        mock_construct.return_value = payload

        client = Client()
        response = client.post(
            '/billing/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_sig'
        )

        assert response.status_code == 200

        profile_with_stripe.refresh_from_db()
        assert profile_with_stripe.subscription_status == 'canceled'
        assert profile_with_stripe.is_subscribed == False


@pytest.mark.django_db
class TestWebhookErrorHandling:
    """Test webhook error handling and retry logic"""

    @patch('stripe.Webhook.construct_event')
    def test_webhook_returns_429_on_rate_limit(self, mock_construct):
        """Rate limit errors should return 429 for retry"""
        mock_construct.side_effect = stripe.error.RateLimitError('rate limited')

        client = Client()
        response = client.post(
            '/billing/webhook/',
            data=json.dumps({}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_sig'
        )

        # Should return 429 to tell Stripe to retry
        assert response.status_code == 429

    @patch('stripe.Webhook.construct_event')
    def test_webhook_returns_503_on_connection_error(self, mock_construct):
        """Connection errors should return 503 for retry"""
        mock_construct.side_effect = ConnectionError('network error')

        client = Client()
        response = client.post(
            '/billing/webhook/',
            data=json.dumps({}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_sig'
        )

        # Should return 503 to tell Stripe to retry
        assert response.status_code == 503

    @patch('stripe.Webhook.construct_event')
    def test_webhook_returns_400_on_invalid_event(self, mock_construct):
        """Invalid events should return 400 (don't retry)"""
        mock_construct.side_effect = ValueError('invalid event')

        client = Client()
        response = client.post(
            '/billing/webhook/',
            data=json.dumps({}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_sig'
        )

        # Should return 400 to tell Stripe not to retry
        assert response.status_code == 400

    def test_webhook_missing_signature_returns_403(self):
        """Missing Stripe signature should return 403"""
        client = Client()
        response = client.post(
            '/billing/webhook/',
            data=json.dumps({}),
            content_type='application/json'
            # No STRIPE_SIGNATURE header
        )

        assert response.status_code == 403
