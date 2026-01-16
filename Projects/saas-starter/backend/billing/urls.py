from django.urls import path
from . import views

urlpatterns = [
    path("pricing/", views.pricing_page, name="pricing"),
    path("checkout/", views.create_checkout_session, name="checkout"),
    path("success/", views.billing_success, name="success"),
    path("cancel/", views.billing_cancel, name="cancel"),
    path("dashboard/", views.billing_dashboard, name="dashboard"),
    path("status/", views.billing_status, name="status"),
    path("portal/", views.customer_portal, name="portal"),
    path("webhook/", views.stripe_webhook, name="webhook"),
]
