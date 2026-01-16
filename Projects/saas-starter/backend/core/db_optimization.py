"""
Database Query Optimization Module
Provides utilities for optimal database queries and performance
"""
from django.contrib.auth.models import User
from users.models import Profile
from billing.models import Subscription, WebhookEvent
from django.db.models import Prefetch, Q


class OptimizedQueryManager:
    """
    Manager for optimized database queries to prevent N+1 and improve performance
    """

    @staticmethod
    def get_user_with_profile(user_id):
        """
        Get user with profile in single query (select_related)
        Prevents N+1 query problem
        """
        return User.objects.select_related('profile').get(id=user_id)

    @staticmethod
    def get_users_with_profiles():
        """
        Get all users with their profiles in optimized query
        Uses select_related to fetch in single query
        """
        return User.objects.select_related('profile').all()

    @staticmethod
    def get_active_subscriptions():
        """
        Get all active subscriptions with user data
        Prevents N+1 queries when accessing user data
        """
        return Subscription.objects.select_related('user').filter(
            status__in=['active', 'trialing']
        )

    @staticmethod
    def get_user_subscription_status(user_id):
        """
        Get user with subscription status in single query
        Used for dashboard/billing pages
        """
        try:
            return User.objects.select_related(
                'profile',
                'subscription'
            ).get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_webhook_events_processed(limit=100):
        """
        Get recent processed webhook events (for monitoring)
        """
        return WebhookEvent.objects.filter(
            processed=True
        ).order_by('-processed_at')[:limit]

    @staticmethod
    def get_webhook_events_failed(limit=50):
        """
        Get webhook events that failed processing (for debugging)
        """
        return WebhookEvent.objects.filter(
            processed=True,
            error_message__isnull=False
        ).order_by('-updated_at')[:limit]

    @staticmethod
    def get_users_by_subscription_status(status):
        """
        Get all users with specific subscription status
        Optimized for billing/reporting
        """
        return User.objects.filter(
            profile__subscription_status=status
        ).select_related('profile').values_list('id', 'email', 'username')

    @staticmethod
    def get_profile_with_all_data(profile_id):
        """
        Get profile with all related data for dashboard
        """
        return Profile.objects.select_related('user').get(id=profile_id)

    @staticmethod
    def bulk_update_subscription_status(user_ids, new_status):
        """
        Bulk update subscription status for multiple users
        Optimized for batch operations
        """
        Profile.objects.filter(
            user_id__in=user_ids
        ).update(subscription_status=new_status)

    @staticmethod
    def get_user_stats():
        """
        Get aggregate stats for dashboard (count, plans distribution)
        Optimized query for analytics
        """
        from django.db.models import Count, Q
        
        total_users = User.objects.count()
        active_subscriptions = Profile.objects.filter(
            subscription_status='active'
        ).count()
        pro_users = Profile.objects.filter(plan='pro').count()
        free_users = Profile.objects.filter(plan='free').count()
        
        return {
            'total_users': total_users,
            'active_subscriptions': active_subscriptions,
            'pro_users': pro_users,
            'free_users': free_users,
            'trial_users': Profile.objects.filter(subscription_status='trialing').count(),
            'past_due_users': Profile.objects.filter(subscription_status='past_due').count(),
        }
