"""
Comprehensive Logging and Monitoring Setup
Tracks performance, errors, and usage patterns
"""

import logging
import json
from datetime import datetime
from django.conf import settings
from django.utils.decorators import decorator_from_middleware
from django.utils.deprecation import MiddlewareNotUsed


# Configure logging for different modules
def setup_logging():
    """Setup comprehensive logging across application"""
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
    )
    
    # Module-specific loggers
    module_loggers = {
        'billing': logging.DEBUG,
        'users': logging.DEBUG,
        'api': logging.DEBUG,
        'core': logging.INFO,
    }
    
    for module_name, level in module_loggers.items():
        logger = logging.getLogger(module_name)
        logger.setLevel(level)
    
    return logging


class RequestLoggingMiddleware:
    """
    Logs all incoming requests with response time and status code
    Useful for performance monitoring and debugging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('api')
    
    def __call__(self, request):
        import time
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Log request details
        log_data = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user': str(request.user) if request.user.is_authenticated else 'anonymous',
        }
        
        # Log at warning level if slow or error
        if response.status_code >= 400:
            self.logger.warning(f"Request error: {json.dumps(log_data)}")
        elif duration > 1:  # Log slow requests
            self.logger.warning(f"Slow request: {json.dumps(log_data)}")
        else:
            self.logger.info(f"Request: {json.dumps(log_data)}")
        
        return response


class PerformanceMetricsMiddleware:
    """
    Tracks and records performance metrics
    Can be sent to monitoring service (Prometheus, CloudWatch, etc)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('performance')
        self.metrics = {
            'requests_total': 0,
            'requests_by_status': {},
            'avg_response_time': 0,
            'slow_requests': [],
        }
    
    def __call__(self, request):
        import time
        
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        # Update metrics
        self.metrics['requests_total'] += 1
        status_code = response.status_code
        self.metrics['requests_by_status'][status_code] = \
            self.metrics['requests_by_status'].get(status_code, 0) + 1
        
        # Track slow requests
        if duration > 1:
            self.metrics['slow_requests'].append({
                'path': request.path,
                'duration': duration,
                'status': status_code,
                'timestamp': datetime.now().isoformat(),
            })
            # Keep only last 100 slow requests
            if len(self.metrics['slow_requests']) > 100:
                self.metrics['slow_requests'] = self.metrics['slow_requests'][-100:]
        
        return response
    
    def get_metrics(self):
        """Get current metrics (can be exposed via /metrics endpoint)"""
        return self.metrics


class ErrorTrackingLogger:
    """
    Captures and logs errors for monitoring
    Can integrate with Sentry, Rollbar, or custom tracking
    """
    
    def __init__(self):
        self.logger = logging.getLogger('error_tracking')
        self.error_count = 0
    
    def log_error(self, error_type, message, context=None):
        """Log error with context for debugging"""
        self.error_count += 1
        
        error_data = {
            'type': error_type,
            'message': message,
            'count': self.error_count,
            'context': context or {},
            'timestamp': datetime.now().isoformat(),
        }
        
        self.logger.error(f"Error tracked: {json.dumps(error_data)}")
    
    def log_webhook_error(self, event_id, event_type, error, user_id=None):
        """Log webhook processing errors"""
        self.log_error(
            'webhook_error',
            f"Failed to process {event_type}",
            {
                'event_id': event_id,
                'event_type': event_type,
                'error': str(error),
                'user_id': user_id,
            }
        )
    
    def log_stripe_error(self, operation, error, user_id=None):
        """Log Stripe API errors"""
        self.log_error(
            'stripe_error',
            f"Stripe {operation} failed",
            {
                'operation': operation,
                'error': str(error),
                'user_id': user_id,
            }
        )


# Global error tracker instance
error_tracker = ErrorTrackingLogger()


def get_logging_config():
    """
    Returns complete logging configuration for settings.py
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/django.log',
                'maxBytes': 1024 * 1024 * 10,  # 10MB
                'backupCount': 5,
                'formatter': 'verbose',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/errors.log',
                'maxBytes': 1024 * 1024 * 10,  # 10MB
                'backupCount': 5,
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            },
            'billing': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'users': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'api': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }
