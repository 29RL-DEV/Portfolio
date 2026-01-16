"""
JWT Authentication with HttpOnly Cookies
============================================
Production-grade authentication with:
- JWT tokens (access + refresh)
- HttpOnly secure cookies (no XSS vulnerability)
- CSRF protection
- Rate limiting on auth endpoints
- Token refresh pattern
"""

import logging
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger("auth")


# ============================================================================
# JWT TOKEN HELPERS
# ============================================================================


class JWTTokenManager:
    """Manage JWT tokens for auth and refresh."""

    # Token expiration times
    ACCESS_TOKEN_EXPIRY = 15 * 60  # 15 minutes
    REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 * 60  # 7 days

    @staticmethod
    def create_access_token(user_id: int) -> str:
        """Create JWT access token."""
        payload = {
            "user_id": user_id,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(seconds=JWTTokenManager.ACCESS_TOKEN_EXPIRY),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create JWT refresh token."""
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(seconds=JWTTokenManager.REFRESH_TOKEN_EXPIRY),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str, token_type: str = "access"):
        """
        Verify JWT token.
        
        Args:
            token: JWT token string
            token_type: "access" or "refresh"
            
        Returns:
            Decoded payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
                
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired {token_type} token")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid {token_type} token: {e}")
            return None


def require_jwt_auth(view_func):
    """Decorator to require valid JWT access token."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get token from Authorization header or cookie
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        token = None
        
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            token = request.COOKIES.get("access_token")
        
        if not token:
            return JsonResponse(
                {"error": "Missing authentication token"},
                status=401,
            )
        
        # Verify token
        payload = JWTTokenManager.verify_token(token, token_type="access")
        if not payload:
            return JsonResponse(
                {"error": "Invalid or expired token"},
                status=401,
            )
        
        # Get user from token
        try:
            user = User.objects.get(id=payload["user_id"])
            request.user = user
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User not found"},
                status=401,
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================


@require_http_methods(["POST"])
@csrf_protect
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def login_view(request):
    """
    Login endpoint.
    
    Returns:
    - access_token (short-lived, in HttpOnly cookie + response)
    - refresh_token (long-lived, in HttpOnly cookie)
    - user info
    """
    import json
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400,
        )
    
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    if not email or not password:
        return JsonResponse(
            {"error": "Email and password are required"},
            status=400,
        )
    
    # Try to authenticate
    # First try with email as username
    user = authenticate(request, username=email, password=password)
    
    if user is None:
        # Try to find by email and authenticate
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    if user is None:
        logger.warning(f"Failed login attempt for email: {email}")
        return JsonResponse(
            {"error": "Invalid email or password"},
            status=401,
        )
    
    if not user.is_active:
        return JsonResponse(
            {"error": "User account is inactive"},
            status=403,
        )
    
    # Create tokens
    access_token = JWTTokenManager.create_access_token(user.id)
    refresh_token = JWTTokenManager.create_refresh_token(user.id)
    
    # Prepare response
    response = JsonResponse(
        {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "access_token": access_token,  # Also in body for flexibility
        },
        status=200,
    )
    
    # Set HttpOnly cookies
    response.set_cookie(
        "access_token",
        access_token,
        max_age=JWTTokenManager.ACCESS_TOKEN_EXPIRY,
        httponly=True,
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite="Lax",
        path="/",
    )
    
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=JWTTokenManager.REFRESH_TOKEN_EXPIRY,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path="/",
    )
    
    logger.info(f"User {user.id} ({user.email}) logged in")
    return response


@require_http_methods(["POST"])
@csrf_protect
@ratelimit(key="ip", rate="10/m", method="POST", block=True)
def refresh_token_view(request):
    """
    Refresh access token using refresh token.
    
    Returns:
    - new access_token (in HttpOnly cookie + response)
    """
    # Get refresh token from cookie or body
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        try:
            import json
            data = json.loads(request.body)
            refresh_token = data.get("refresh_token")
        except json.JSONDecodeError:
            pass
    
    if not refresh_token:
        return JsonResponse(
            {"error": "Missing refresh token"},
            status=401,
        )
    
    # Verify refresh token
    payload = JWTTokenManager.verify_token(refresh_token, token_type="refresh")
    if not payload:
        return JsonResponse(
            {"error": "Invalid or expired refresh token"},
            status=401,
        )
    
    # Get user
    try:
        user = User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"},
            status=401,
        )
    
    # Create new access token
    new_access_token = JWTTokenManager.create_access_token(user.id)
    
    # Prepare response
    response = JsonResponse(
        {
            "success": True,
            "access_token": new_access_token,
        },
        status=200,
    )
    
    # Update HttpOnly cookie
    response.set_cookie(
        "access_token",
        new_access_token,
        max_age=JWTTokenManager.ACCESS_TOKEN_EXPIRY,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        path="/",
    )
    
    logger.info(f"Token refreshed for user {user.id}")
    return response


@require_http_methods(["POST"])
@csrf_protect
def logout_view(request):
    """
    Logout endpoint.
    Clears tokens from cookies.
    """
    response = JsonResponse(
        {
            "success": True,
            "message": "Logged out successfully",
        },
        status=200,
    )
    
    # Clear tokens from cookies
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    
    logger.info(f"User logged out")
    return response


@require_http_methods(["GET"])
@require_jwt_auth
def current_user_view(request):
    """Get current authenticated user info."""
    user = request.user
    profile = user.profile
    
    return JsonResponse(
        {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "profile": {
                "plan": profile.plan,
                "is_subscribed": profile.is_subscribed,
                "subscription_status": profile.subscription_status,
                "is_active": profile.is_active(),
            },
        },
        status=200,
    )
