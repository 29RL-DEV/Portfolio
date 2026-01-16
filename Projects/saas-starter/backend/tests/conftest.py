import pytest
from django.contrib.auth.models import User
from users.models import Profile
from billing.models import WebhookEvent


@pytest.fixture
def user(db):
    """Create test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def profile_with_stripe(db, user):
    """Create profile with Stripe customer"""
    profile = user.profile
    profile.stripe_customer_id = 'cus_test123'
    profile.stripe_subscription_id = 'sub_test123'
    profile.subscription_status = 'active'
    profile.is_subscribed = True
    profile.save()
    return profile


@pytest.fixture
def stripe_webhook_payload():
    """Sample Stripe webhook"""
    return {
        'id': 'evt_test123',
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'id': 'cs_test123',
                'customer': 'cus_test123',
                'subscription': 'sub_test123',
                'metadata': {'user_id': '1'}
            }
        }
    }


@pytest.fixture
def webhook_event(db):
    """Create sample webhook event"""
    return WebhookEvent.objects.create(
        event_id='evt_test123',
        event_type='checkout.session.completed',
        processed=False
    )
