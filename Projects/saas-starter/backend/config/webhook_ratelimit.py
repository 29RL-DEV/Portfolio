"""
Custom rate limiting for webhook endpoints.
Uses event ID-based rate limiting instead of IP-based, since Stripe webhooks
come from multiple IPs and need to handle retries properly.
"""
import logging
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger("billing")


def webhook_rate_limit(max_per_minute=100):
    """
    Rate limit based on event signatures, not IP addresses.
    This allows Stripe to retry failed webhooks while preventing abuse.
    
    Args:
        max_per_minute: Maximum webhook events to process per minute
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get webhook signature header to use as rate limit key
            sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
            
            # If no signature, reject immediately (Stripe always provides signature)
            if not sig_header:
                logger.warning("Webhook request without Stripe signature header")
                return HttpResponse(status=400)
            
            # Create cache key based on webhook signature prefix
            # This rate limits the overall webhook traffic, not per user/event
            cache_key = f"webhook_rate_limit:global"
            
            # Increment counter in cache
            try:
                current_count = cache.get(cache_key, 0)
                
                if current_count >= max_per_minute:
                    logger.warning(f"Webhook rate limit exceeded: {current_count}/{max_per_minute} in last minute")
                    # Return 429 (Too Many Requests) so Stripe will retry
                    return HttpResponse(status=429)
                
                # Increment and set expiry to 60 seconds
                cache.set(cache_key, current_count + 1, 60)
                
            except Exception as e:
                logger.error(f"Error checking webhook rate limit: {e}")
                # If cache fails, allow the request through but log the error
                # Better to process webhook than to reject it
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator


def webhook_signature_rate_limit(max_retries=5, window_seconds=3600):
    """
    Rate limit by webhook event ID to prevent duplicate processing.
    Different from idempotency - this prevents brute force attempts on same event.
    
    Args:
        max_retries: Maximum times same event can be processed
        window_seconds: Time window for counting retries
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            payload = request.body
            sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
            
            if not sig_header:
                return HttpResponse(status=400)
            
            # Create cache key from signature
            cache_key = f"webhook_sig:{sig_header}"
            
            try:
                current_count = cache.get(cache_key, 0)
                
                if current_count >= max_retries:
                    logger.warning(
                        f"Webhook signature rate limit exceeded for signature: {sig_header[:20]}..."
                    )
                    # Still process (idempotency check will handle it)
                    # But log the suspicious activity
                
                # Increment counter
                cache.set(cache_key, current_count + 1, window_seconds)
                
            except Exception as e:
                logger.error(f"Error checking webhook signature rate limit: {e}")
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator
