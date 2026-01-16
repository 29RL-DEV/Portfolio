from django.urls import path
from .views import home, pro_feature, healthcheck, api_login
from .auth import login_view, refresh_token_view, logout_view, current_user_view
from .billing_api import cancel_subscription, delete_account, export_account_data

urlpatterns = [
    # Main views
    path("", home, name="home"),
    path("pro/", pro_feature, name="pro"),
    path("health/", healthcheck, name="healthcheck"),
    
    # Legacy API login (kept for backwards compatibility)
    path("api/login/", api_login, name="api_login"),
    
    # JWT Authentication
    path("auth/login/", login_view, name="jwt_login"),
    path("auth/refresh/", refresh_token_view, name="jwt_refresh"),
    path("auth/logout/", logout_view, name="jwt_logout"),
    path("auth/me/", current_user_view, name="current_user"),
    
    # Billing API
    path("billing/cancel/", cancel_subscription, name="cancel_subscription"),
    
    # GDPR/Account Management
    path("account/delete/", delete_account, name="delete_account"),
    path("account/export/", export_account_data, name="export_account_data"),
]
