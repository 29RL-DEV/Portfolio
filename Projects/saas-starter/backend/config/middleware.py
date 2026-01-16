"""
Middleware pentru gestionarea automată a HTTPS în development și production.
Redirecționează automat cererile HTTPS către HTTP în development.
"""
import logging
from django.http import HttpResponsePermanentRedirect
from django.conf import settings

logger = logging.getLogger(__name__)


class HTTPSRedirectMiddleware:
    """
    Middleware care gestionează automat HTTPS:
    - În development: redirecționează HTTPS -> HTTP (pentru a evita erorile)
    - În production: lasă HTTPS să funcționeze normal (gestionat de reverse proxy)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # În development, dacă cererea vine prin HTTPS, redirecționează către HTTP
        if settings.DEBUG and request.scheme == 'https':
            http_url = request.build_absolute_uri().replace('https://', 'http://', 1)
            logger.debug(f"Redirecting HTTPS to HTTP in development: {http_url}")
            return HttpResponsePermanentRedirect(http_url)
        
        response = self.get_response(request)
        return response


class SecurityHeadersMiddleware:
    """
    Middleware pentru adăugare HTTP security headers.
    Protejează contra XSS, clickjacking, MIME type sniffing, etc.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection (browser built-in)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature policy (modern browsers)
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy (basic - adjust as needed)
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.stripe.com; "
                "font-src 'self' data:; "
                "frame-src https://js.stripe.com;"
            )
        
        return response
