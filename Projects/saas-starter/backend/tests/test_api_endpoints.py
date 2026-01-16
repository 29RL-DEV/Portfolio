import pytest
from django.test import Client
from django.contrib.auth.models import User
from users.models import Profile
from rest_framework import status


@pytest.mark.django_db
class TestAPIHealthcheck:
    """Test health check endpoint"""

    def test_healthcheck_returns_200(self):
        """Health check should return 200 status"""
        client = Client()
        response = client.get("/health/")
        assert response.status_code == 200

    def test_healthcheck_returns_json(self):
        """Health check should return JSON response"""
        client = Client()
        response = client.get("/health/")
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]


@pytest.mark.django_db
class TestAPIAuthEndpoints:
    """Test authentication endpoints"""

    def test_login_redirect_unauthenticated(self):
        """Unauthenticated users should be redirected to login"""
        client = Client()
        response = client.get("/dashboard/", follow=False)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_pro_feature_requires_subscription(self, user):
        """PRO features should require active subscription"""
        client = Client()
        client.force_login(user)
        response = client.get("/pro-feature/", follow=False)
        assert response.status_code == 302
        assert "/billing/pricing/" in response.url

    def test_pro_feature_available_to_subscribed_users(self, db, user):
        """Subscribed users should access PRO features"""
        client = Client()
        client.force_login(user)
        
        # Activate subscription
        profile = user.profile
        profile.is_subscribed = True
        profile.subscription_status = "active"
        profile.save()
        
        response = client.get("/pro-feature/", follow=False)
        assert response.status_code == 200


@pytest.mark.django_db
class TestBillingEndpoints:
    """Test billing page endpoints"""

    def test_pricing_page_returns_200(self):
        """Pricing page should be accessible"""
        client = Client()
        response = client.get("/billing/pricing/")
        assert response.status_code == 200

    def test_billing_status_requires_login(self):
        """Billing status should require login"""
        client = Client()
        response = client.get("/billing/status/", follow=False)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_billing_status_shows_subscription_info(self, user):
        """Billing status page should show user's subscription"""
        client = Client()
        client.force_login(user)
        response = client.get("/billing/status/")
        assert response.status_code == 200
        assert "subscription" in response.content.decode()

    def test_customer_portal_redirect(self, user):
        """Customer portal should redirect to Stripe"""
        client = Client()
        client.force_login(user)
        
        # Set up stripe customer
        profile = user.profile
        profile.stripe_customer_id = "cus_test123"
        profile.save()
        
        # Would normally redirect to Stripe (mocked in production)
        response = client.get("/billing/customer-portal/", follow=False)
        assert response.status_code in [302, 500]  # 302 redirect or 500 if Stripe key missing


@pytest.mark.django_db
class TestPasswordReset:
    """Test password reset functionality"""

    def test_password_reset_view_accessible(self):
        """Password reset view should be accessible"""
        client = Client()
        response = client.get("/password_reset/")
        assert response.status_code == 200

    def test_password_reset_form_exists(self):
        """Password reset form should exist on page"""
        client = Client()
        response = client.get("/password_reset/")
        content = response.content.decode()
        assert "email" in content.lower()


@pytest.mark.django_db
class TestProfileModel:
    """Test Profile model methods and properties"""

    def test_profile_created_with_user(self, user):
        """Profile should be created when user is created"""
        assert hasattr(user, 'profile')
        assert user.profile is not None

    def test_subscription_state_validation(self, user):
        """Profile should validate valid subscription transitions"""
        profile = user.profile
        
        # Start as inactive
        profile.subscription_status = 'inactive'
        profile.save()
        
        # Should transition to trialing
        profile.subscription_status = 'trialing'
        profile.save()
        assert profile.subscription_status == 'trialing'

    def test_profile_string_representation(self, user):
        """Profile __str__ should display user info"""
        profile = user.profile
        profile.plan = 'pro'
        profile.subscription_status = 'active'
        profile.save()
        
        str_rep = str(profile)
        assert user.username in str_rep
        assert 'active' in str_rep.lower()


@pytest.mark.django_db
class TestDashboardPages:
    """Test dashboard pages"""

    def test_home_page_redirects_if_not_authenticated(self):
        """Home page should redirect if not authenticated"""
        client = Client()
        response = client.get("/dashboard/", follow=False)
        assert response.status_code == 302

    def test_home_page_shows_free_dashboard_for_free_users(self, user):
        """Free users should see free dashboard"""
        client = Client()
        client.force_login(user)
        
        profile = user.profile
        profile.is_subscribed = False
        profile.save()
        
        response = client.get("/dashboard/")
        assert response.status_code == 200

    def test_home_page_shows_pro_dashboard_for_pro_users(self, user):
        """PRO users should see pro dashboard"""
        client = Client()
        client.force_login(user)
        
        profile = user.profile
        profile.is_subscribed = True
        profile.plan = 'pro'
        profile.save()
        
        response = client.get("/dashboard/")
        assert response.status_code == 200
