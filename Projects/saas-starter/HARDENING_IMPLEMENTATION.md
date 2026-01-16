# Production Hardening Implementation Guide

This document covers all the production-grade security features added to the SaaS application.

## 📋 Table of Contents

1. [New Features Overview](#new-features-overview)
2. [Environment Variables](#environment-variables)
3. [API Endpoints](#api-endpoints)
4. [Security Features](#security-features)
5. [Testing](#testing)
6. [Deployment Checklist](#deployment-checklist)

---

## New Features Overview

### 1. ✅ Webhook Hardening (`backend/billing/webhooks.py`)

- **Purpose**: Production-grade Stripe webhook processing
- **Key Features**:
  - Cryptographic signature verification using `STRIPE_WEBHOOK_SECRET`
  - Idempotency protection (no duplicate processing)
  - Atomic database transactions
  - Comprehensive error handling
  - GDPR compliant (no PII storage)
  - Stripe as authoritative source for subscription state

**Usage**: Automatically called from `billing/views.py` webhook endpoint.

### 2. ✅ Subscription Cancellation API (`POST /api/billing/cancel/`)

- **Purpose**: Allow users to cancel subscriptions safely
- **Authentication**: Required (login_required)
- **Rate Limit**: 5 requests per hour per user
- **Returns**: JSON response with status
- **Behavior**:
  - Calls Stripe to cancel at period end (not immediately)
  - Updates `Profile.plan = "free"`
  - Updates `Profile.subscription_status = "canceled"`
  - Keeps user account alive
  - Sends cancellation email

### 3. ✅ GDPR Compliance Endpoints

#### Account Deletion (`POST /api/account/delete/`)

- **Purpose**: Allow users to delete their account (GDPR Right to be Forgotten)
- **Authentication**: Required
- **Rate Limit**: 1 request per hour per user
- **Deletes**:
  - User account
  - Profile
  - Stripe customer (if exists)
  - Associated webhook events
- **Returns**: Success message

#### Account Data Export (`GET /api/account/export/`)

- **Purpose**: Allow users to export their personal data (GDPR Right of Access)
- **Authentication**: Required
- **Rate Limit**: 10 requests per hour per user
- **Exports**:
  - User information
  - Profile subscription data
  - Billing history from Stripe
  - All returned as downloadable JSON file
- **Format**: JSON file named `account-export-{user_id}.json`

### 4. ✅ JWT Authentication with HttpOnly Cookies (`backend/api/auth.py`)

- **Purpose**: Secure authentication without XSS vulnerabilities
- **Key Features**:
  - JWT tokens for stateless authentication
  - HttpOnly secure cookies (XSS resistant)
  - Refresh token pattern (7-day refresh, 15-minute access)
  - CSRF protection
  - Rate limiting on auth endpoints

**Endpoints**:

- `POST /auth/login/` - Login with email/password
- `POST /auth/refresh/` - Refresh access token
- `POST /auth/logout/` - Logout (clears cookies)
- `GET /auth/me/` - Get current user info

### 5. ✅ Rate Limiting Applied to All Endpoints

- **Login**: 5 requests/minute per IP
- **Password Reset**: 3 requests/hour per IP
- **Webhook**: 100 requests/minute per origin
- **Cancel Subscription**: 5 requests/hour per user
- **Delete Account**: 1 request/hour per user
- **Export Data**: 10 requests/hour per user
- **Token Refresh**: 10 requests/minute per IP

### 6. ✅ Production Lockdown Settings

- **DEBUG**: Must be `False` in production
- **SECURE_SSL_REDIRECT**: Enabled (HTTP → HTTPS)
- **SESSION_COOKIE_SECURE**: HttpOnly + Secure flags
- **HSTS**: 1 year pre-load ready
- **CORS**: Locked to specific frontend origins
- **ALLOWED_HOSTS**: Required and validated
- **SECRET_KEY**: Required and validated

---

## Environment Variables

### 🔒 REQUIRED for Production

```bash
# Django Core
SECRET_KEY=<strong-random-key>          # Generate: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DEBUG=False                             # MUST be False in production
ALLOWED_HOSTS=yourdomain.com,...        # Comma-separated domains

# Stripe Configuration (LIVE KEYS in production)
STRIPE_PUBLIC_KEY=pk_live_...          # Live public key
STRIPE_SECRET_KEY=sk_live_...          # Live secret key (keep secret!)
STRIPE_WEBHOOK_SECRET=whsec_...        # Webhook signing secret
STRIPE_PRICE_ID=price_...              # Your subscription price ID

# CORS and CSRF Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com,...   # Frontend domains
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,...   # Frontend domains
```

### 📧 Email Configuration

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Use app-specific password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### 🔴 HIGHLY RECOMMENDED for Production

```bash
# Redis (required for distributed rate limiting)
REDIS_URL=redis://username:password@host:6379/0

# Database (don't use SQLite in production)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Error Tracking
SENTRY_DSN=https://...@sentry.io/...
```

### 🟡 Optional

```bash
# AWS S3 for file storage
AWS_STORAGE_BUCKET_NAME=bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# OpenAI API for AI features
OPENAI_API_KEY=sk_...

# Logging
DJANGO_LOG_LEVEL=INFO
```

---

## API Endpoints

### Authentication

```bash
# POST /auth/login/
# Body: {"email": "user@example.com", "password": "..."}
# Returns: {access_token, user info, sets HttpOnly cookies}

# POST /auth/refresh/
# Refreshes access token using refresh_token cookie
# Returns: {new access_token, updates HttpOnly cookie}

# POST /auth/logout/
# Clears authentication cookies
# Returns: {success message}

# GET /auth/me/
# Requires: Authorization header or access_token cookie
# Returns: {user info, profile subscription data}
```

### Billing

```bash
# POST /billing/cancel/
# Requires: Authentication
# Rate limit: 5/hour per user
# Returns: {success, message about billing period}

# POST /account/delete/
# Requires: Authentication
# Rate limit: 1/hour per user
# Returns: {success message}

# GET /account/export/
# Requires: Authentication
# Rate limit: 10/hour per user
# Returns: {JSON file download with all user data}
```

---

## Security Features

### 🔐 Webhook Signature Verification

```python
# All Stripe webhooks are verified using STRIPE_WEBHOOK_SECRET
# Invalid signatures are rejected with 403 Forbidden
# Prevents webhook spoofing attacks
```

### 🔄 Idempotency Protection

```python
# Each webhook event is stored with unique event_id
# Duplicate events are skipped (no double-charging)
# WebhookEvent model prevents race conditions
```

### 🚫 Rate Limiting

```python
# Prevents brute force attacks on:
# - Login attempts
# - Password reset requests
# - Webhook processing
# - Account deletion
# Uses Redis for distributed rate limiting (or LocMemCache for dev)
```

### 🔒 HttpOnly Cookies

```python
# Authentication tokens stored in HttpOnly cookies
# Cannot be accessed via JavaScript (prevents XSS theft)
# Secure flag set in production (HTTPS only)
# SameSite=Lax prevents CSRF attacks
```

### 🛡️ CSRF Protection

```python
# All state-changing endpoints (POST, PUT, DELETE) require CSRF token
# Token automatically included in forms and API calls
# SameSite cookie policy prevents cross-origin requests
```

### 📊 GDPR Compliance

```python
# Account deletion removes all personal data
# Account export provides all data in portable format
# WebhookEvent model never stores PII
# Event data hashed for verification only
```

---

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python manage.py test tests.test_hardening_features -v 2

# Run specific test class
python manage.py test tests.test_hardening_features.WebhookIdempotencyTest -v 2

# Run with coverage
coverage run --source='.' manage.py test tests.test_hardening_features
coverage report
```

### Test Coverage Includes:

- ✅ Webhook idempotency (duplicate event prevention)
- ✅ Subscription status updates
- ✅ Subscription cancellation workflow
- ✅ GDPR account deletion
- ✅ GDPR account export
- ✅ JWT token creation and verification
- ✅ Rate limiting decorators
- ✅ Status mapping (Stripe → Profile)

---

## Deployment Checklist

### Pre-Deployment

- [ ] Set `DEBUG=False`
- [ ] Generate and set strong `SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS` with your domain(s)
- [ ] Update `CORS_ALLOWED_ORIGINS` with frontend domain(s)
- [ ] Update `CSRF_TRUSTED_ORIGINS` with frontend domain(s)
- [ ] Set up PostgreSQL database (don't use SQLite)
- [ ] Set up Redis for rate limiting (optional but recommended)
- [ ] Configure all Stripe keys (LIVE mode)
- [ ] Set up email configuration
- [ ] Set up error tracking (Sentry recommended)
- [ ] Test webhooks with Stripe CLI

### Deployment Steps

```bash
# 1. Set environment variables in production environment
export SECRET_KEY=<generated-key>
export DEBUG=False
export ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
export STRIPE_SECRET_KEY=sk_live_...
# ... etc

# 2. Run migrations
python manage.py migrate

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Run tests
python manage.py test tests.test_hardening_features -v 2

# 5. Start application
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Post-Deployment

- [ ] Test webhook delivery with Stripe test events
- [ ] Test login/logout flow
- [ ] Test cancellation flow
- [ ] Test GDPR delete/export endpoints
- [ ] Verify HTTPS redirect
- [ ] Verify security headers (`X-Frame-Options`, etc.)
- [ ] Monitor error logs (Sentry)
- [ ] Verify rate limiting works
- [ ] Test with real Stripe live mode (small amount)

---

## Production Safety Features

### Stripe Integration Safety

1. **Signature Verification**: All webhooks signed with `STRIPE_WEBHOOK_SECRET`
2. **Idempotency**: No duplicate processing even if Stripe retries
3. **Source of Truth**: Profile always updated from Stripe, never from local state alone
4. **Error Handling**: Failed requests are logged but don't break the flow
5. **Retry Logic**: Failed operations allow Stripe to retry safely

### Account Security

1. **HttpOnly Cookies**: Authentication tokens cannot be stolen via XSS
2. **CSRF Protection**: State-changing requests verified with CSRF token
3. **Rate Limiting**: Prevents brute force and abuse
4. **Password Validation**: Enforces strong password requirements
5. **Session Security**: Secure and HttpOnly cookie flags

### Data Protection

1. **GDPR Delete**: Complete account and data removal
2. **GDPR Export**: User-portable data in JSON format
3. **PII Security**: No personal data stored in webhook events
4. **Encryption**: HTTPS enforced in production
5. **HSTS**: Browsers remember HTTPS requirement

---

## Monitoring & Observability

### Logs to Monitor

```python
# Billing operations
logger = logging.getLogger('billing')

# Auth operations
logger = logging.getLogger('auth')

# Config operations
logger = logging.getLogger('config')
```

### Key Metrics to Track

- Webhook processing latency
- Webhook error rate
- Authentication success/failure rate
- Rate limit hit rate
- Stripe API call latency
- Database query performance

### Sentry Integration

Set `SENTRY_DSN` to automatically track:

- Webhook processing errors
- Authentication failures
- Database errors
- API errors
- Rate limit violations

---

## Troubleshooting

### Webhook Issues

**Problem**: Webhooks not received

- **Solution**: Verify `STRIPE_WEBHOOK_SECRET` is correct
- **Debug**: Check logs for signature verification errors

**Problem**: Duplicate webhook processing

- **Solution**: Check `WebhookEvent` model for existing event_id
- **Debug**: Query database: `WebhookEvent.objects.filter(event_id='...')`

### Authentication Issues

**Problem**: JWT token validation failing

- **Solution**: Verify `SECRET_KEY` is consistent across deployments
- **Debug**: Check token expiry and signature

**Problem**: HttpOnly cookie not set

- **Solution**: Ensure `DEBUG=False` in production
- **Debug**: Check response headers in browser dev tools

### Rate Limiting Issues

**Problem**: Rate limiting not working

- **Solution**: If using LocMemCache, only works in single-process
- **Fix**: Set up Redis for production

---

## References

- [Stripe Webhook Documentation](https://stripe.com/docs/webhooks)
- [Django Security Documentation](https://docs.djangoproject.com/en/4.2/topics/security/)
- [GDPR Compliance Guide](https://gdpr-info.eu/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Rate Limiting](https://django-ratelimit.readthedocs.io/)

---

**Last Updated**: January 15, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
