from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger("users")


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class RateLimitedLoginView(LoginView):
    template_name = 'registration/login.html'


@method_decorator(ratelimit(key='ip', rate='3/h', method='POST', block=True), name='post')
class RateLimitedPasswordResetView(PasswordResetView):
    """
    Allow users to request password reset with rate limiting (3 per hour per IP).
    Sends email with reset link.
    """
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    
    def form_valid(self, form):
        """Log password reset requests"""
        logger.info(f"Password reset requested for email: {form.cleaned_data.get('email')}")
        return super().form_valid(form)


@method_decorator(ratelimit(key='ip', rate='10/h', method='POST', block=True), name='post')
class RateLimitedPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Confirm password reset with rate limiting (10 per hour per IP).
    """
    template_name = 'registration/password_reset_confirm.html'
    
    def form_valid(self, form):
        """Log successful password resets"""
        logger.info(f"Password reset successful for user: {self.request.user}")
        return super().form_valid(form)
