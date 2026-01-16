from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from users import views as user_views
from users.auth_views import RateLimitedLoginView, RateLimitedPasswordResetView, RateLimitedPasswordResetConfirmView

urlpatterns = [
    path("admin/", admin.site.urls),
    # User registration/signup
    path("signup/", user_views.signup, name="signup"),
    # Custom login with rate limiting
    path("login/", RateLimitedLoginView.as_view(), name="login"),
    # Password reset with rate limiting
    path("password_reset/", RateLimitedPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", TemplateView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", RateLimitedPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", TemplateView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),
    # Stripe billing
    path("billing/", include("billing.urls")),
    # AI Core endpoints
    path("", include("core.urls")),
    # Contact form
    path("contact/", user_views.contact_form, name="contact"),
    # Legal pages
    path("terms/", TemplateView.as_view(template_name="terms.html"), name="terms"),
    path(
        "privacy/", TemplateView.as_view(template_name="privacy.html"), name="privacy"
    ),
    path(
        "cookies/", TemplateView.as_view(template_name="cookies.html"), name="cookies"
    ),
]
