from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from functools import wraps
from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger("api")


def require_pro(view_func):
    """Decorator to protect PRO features - redirect to pricing if not subscribed"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/login/?next={request.path}")
        
        profile = request.user.profile
        
        # Check if subscription is active (not just is_subscribed boolean)
        if not profile.is_active():
            return redirect("/billing/pricing/")
        
        return view_func(request, *args, **kwargs)
    return wrapper


class ProMiddleware:
    """Middleware to check PRO status for protected routes"""
    def __init__(self, get_response):
        self.get_response = get_response
        # Routes that require PRO subscription
        self.protected_routes = ['/pro/']

    def __call__(self, request):
        # Check if route requires PRO
        for route in self.protected_routes:
            if request.path.startswith(route):
                if not request.user.is_authenticated:
                    return redirect(f"/login/?next={request.path}")
                
                profile = request.user.profile
                if not profile.is_active():
                    return redirect("/billing/pricing/")

        response = self.get_response(request)
        return response


@login_required
def home(request):
    """Home page - shows different dashboard based on subscription status"""
    # Use select_related to avoid N+1 queries
    user = request.user
    if hasattr(user, '_profile_cache'):
        profile = user._profile_cache
    else:
        profile = user.profile
    
    if profile.is_subscribed:
        return render(request, "dashboard_pro.html")
    return render(request, "dashboard_free.html")


@login_required
@require_pro
def pro_feature(request):
    """PRO feature page - protected by require_pro decorator"""
    return render(request, "pro_feature.html")


def healthcheck(request):
    """
    Health check endpoint for load balancers and uptime monitors.
    Returns 200 if app is healthy, 503 if there are issues.
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            "status": "healthy",
            "service": "SaaS Platform",
            "database": "connected",
        }, status=200)
    
    except OperationalError as e:
        logger.error(f"Database connection failed in health check: {e}")
        return JsonResponse({
            "status": "unhealthy",
            "service": "SaaS Platform",
            "database": "disconnected",
            "error": "Database connection failed"
        }, status=503)
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JsonResponse({
            "status": "unhealthy",
            "service": "SaaS Platform",
            "error": str(e)
        }, status=503)


@api_view(["POST"])
def api_login(request):
    """API endpoint for frontend login"""
    email = request.data.get("email")
    password = request.data.get("password")
    
    if not email or not password:
        return Response(
            {"error": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Try to authenticate - Django's authenticate can use email if configured
    # First try with email as username
    user = authenticate(request, username=email, password=password)
    
    # If that fails, try to find user by email
    if user is None:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    if user is not None:
        login(request, user)
        return Response({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )
