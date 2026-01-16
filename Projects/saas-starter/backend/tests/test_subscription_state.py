import pytest
from django.core.exceptions import ValidationError
from users.models import Profile


@pytest.mark.django_db
class TestSubscriptionStateMachine:
    """Test subscription state transitions"""

    def test_profile_can_transition_to_active(self, profile_with_stripe):
        """Profile should transition from inactive to active"""
        profile = profile_with_stripe
        profile.subscription_status = 'inactive'
        profile.is_subscribed = False
        profile.save()

        # Update status
        profile.set_subscription_status('active')

        assert profile.subscription_status == 'active'
        assert profile.is_subscribed == True

    def test_inactive_to_trialing_allowed(self, profile_with_stripe):
        """inactive -> trialing allowed (trial period)"""
        profile = profile_with_stripe
        profile.subscription_status = 'inactive'
        profile.is_subscribed = False
        profile.save()

        profile.set_subscription_status('trialing')
        assert profile.subscription_status == 'trialing'
        assert profile.is_subscribed == True

    def test_invalid_transition_raises_error(self, profile_with_stripe):
        """Invalid transitions should raise error"""
        profile = profile_with_stripe
        profile.subscription_status = 'inactive'
        profile.save()

        # inactive -> unpaid is invalid
        with pytest.raises(ValidationError):
            profile.set_subscription_status('unpaid')

    def test_past_due_to_active_allowed(self, profile_with_stripe):
        """past_due -> active allowed (payment recovered)"""
        profile = profile_with_stripe
        profile.subscription_status = 'past_due'
        profile.save()

        profile.set_subscription_status('active')
        assert profile.subscription_status == 'active'

    def test_active_to_canceled_allowed(self, profile_with_stripe):
        """active -> canceled allowed (user cancels)"""
        profile = profile_with_stripe
        profile.subscription_status = 'active'
        profile.is_subscribed = True
        profile.save()

        profile.set_subscription_status('canceled')
        assert profile.subscription_status == 'canceled'
        assert profile.is_subscribed == False

    def test_canceled_to_active_allowed(self, profile_with_stripe):
        """canceled -> active allowed (reactivation)"""
        profile = profile_with_stripe
        profile.subscription_status = 'canceled'
        profile.is_subscribed = False
        profile.save()

        profile.set_subscription_status('active')
        assert profile.subscription_status == 'active'
        assert profile.is_subscribed == True

    def test_update_subscription_status_from_stripe(self, profile_with_stripe):
        """update_subscription_status should use state machine"""
        profile = profile_with_stripe
        profile.subscription_status = 'active'
        profile.save()

        # Stripe says past_due
        profile.update_subscription_status('past_due')
        assert profile.subscription_status == 'past_due'
        assert profile.is_subscribed == True

    def test_active_to_past_due_allowed(self, profile_with_stripe):
        """active -> past_due allowed (payment failed)"""
        profile = profile_with_stripe
        profile.subscription_status = 'active'
        profile.save()

        profile.set_subscription_status('past_due')
        assert profile.subscription_status == 'past_due'
        # past_due is still considered subscribed
        assert profile.is_subscribed == True

    def test_trialing_to_active_allowed(self, profile_with_stripe):
        """trialing -> active allowed (trial period ends)"""
        profile = profile_with_stripe
        profile.subscription_status = 'trialing'
        profile.save()

        profile.set_subscription_status('active')
        assert profile.subscription_status == 'active'
        assert profile.is_subscribed == True

    def test_subscription_status_choices_valid(self, profile_with_stripe):
        """All subscription status choices should be valid"""
        profile = profile_with_stripe

        valid_statuses = [choice[0] for choice in Profile.SUBSCRIPTION_STATUS_CHOICES]
        # inactive should be a valid choice
        assert 'inactive' in valid_statuses
        assert 'active' in valid_statuses
        assert 'canceled' in valid_statuses
