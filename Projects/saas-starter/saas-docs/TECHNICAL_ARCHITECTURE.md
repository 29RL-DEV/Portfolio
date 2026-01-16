# 🏗️ TECHNICAL ARCHITECTURE

**Document Version:** 1.0  
**Last Updated:** January 15, 2026  
**Status:** Production Ready ✅

---

## TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Database Design](#database-design)
5. [API Architecture](#api-architecture)
6. [Security Architecture](#security-architecture)
7. [Deployment Architecture](#deployment-architecture)
8. [Scaling & Performance](#scaling--performance)

---

## SYSTEM OVERVIEW

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│              Runs on separate port (3000)                │
│        - Single Page Application (SPA)                   │
│        - REST API client communication                   │
│        - Token-based authentication                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS REST API
┌────────────────────▼────────────────────────────────────┐
│              Backend (Django)                            │
│          Port 8000 (via Gunicorn)                        │
│    - Subscription management                            │
│    - Stripe payment processing                          │
│    - User authentication                                │
│    - AI features (optional OpenAI)                      │
└────────┬─────────────────┬──────────────────┬───────────┘
         │                 │                  │
    ┌────▼────┐    ┌──────▼───────┐   ┌──────▼────┐
    │PostgreSQL│   │Redis Cache   │   │Stripe API │
    │Database  │   │(Optional)    │   │Webhooks   │
    └──────────┘   └──────────────┘   └───────────┘
```

### Technology Stack

#### Backend

- **Framework:** Django 4.2.10
- **API:** Django REST Framework 3.14.0
- **Database:** PostgreSQL (production) / SQLite (dev)
- **Caching:** Redis 5.0.1 (optional)
- **Task Queue:** Celery (optional)
- **WSGI Server:** Gunicorn 21.2.0
- **Email:** SMTP (Gmail, SendGrid, etc.)

#### Frontend

- **Framework:** React (modern with hooks)
- **Build Tool:** (Vite or Create React App)
- **HTTP Client:** Axios or Fetch API
- **Styling:** CSS Modules or Tailwind
- **State Management:** React Context

#### Infrastructure

- **Deployment:** Docker + Docker Compose
- **Reverse Proxy:** Nginx (production)
- **SSL/TLS:** Let's Encrypt (automatic)
- **File Storage:** AWS S3 (optional)
- **Error Tracking:** Sentry (optional)
- **Logging:** Structured JSON logging

---

## BACKEND ARCHITECTURE

### Project Structure

```
backend/
├── config/
│   ├── settings.py          # Main configuration
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI entry point
│   ├── asgi.py              # ASGI entry point
│   ├── middleware.py        # Custom middleware
│   ├── logging_setup.py     # Logging configuration
│   ├── logging_filters.py   # Logging filters
│   └── webhook_ratelimit.py # Webhook rate limiting
├── api/
│   ├── models.py
│   ├── views.py             # API views (includes decorators)
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   └── migrations/
├── users/
│   ├── models.py            # User & Profile models
│   ├── views.py
│   ├── auth_views.py        # Authentication views
│   ├── signals.py           # Post-save signals
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   ├── management/          # Custom commands
│   └── migrations/
├── billing/
│   ├── models.py            # Subscription & WebhookEvent
│   ├── views.py             # Billing views (pricing, portal)
│   ├── stripe_webhooks.py   # Stripe webhook handlers
│   ├── dunning.py           # Failed payment handling
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   ├── management/
│   └── migrations/
├── core/
│   ├── views_ai.py          # AI feature views
│   ├── ai.py                # AI logic (OpenAI integration)
│   ├── db_optimization.py   # Database query optimization
│   └── urls.py
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── test_api_endpoints.py
│   ├── test_billing_webhooks.py
│   ├── test_subscription_state.py
│   └── __init__.py
├── templates/
│   ├── base.html            # Base template
│   ├── dashboard.html       # Dashboard
│   ├── billing.html         # Billing page
│   ├── pricing.html         # Pricing page
│   ├── error_pages/         # 400, 403, 404, 500
│   ├── email/               # Email templates
│   │   ├── payment_failed.html
│   │   ├── subscription_canceled.html
│   │   └── trial_ending_soon.html
│   └── registration/        # Auth templates
├── static/                  # CSS, JS, images
├── requirements.txt
├── manage.py
├── pytest.ini
└── runtime.txt
```

### Authentication & Authorization

#### User Model

```python
User (Django built-in)
├── username
├── email
├── password (hashed)
├── is_active
├── is_staff
└── Profile (OneToOneField)
    ├── subscription (OneToOneField to Subscription)
    ├── is_subscribed (boolean)
    ├── trial_end_date
    └── created_at
```

#### Subscription Model

```python
Subscription
├── user (OneToOneField)
├── stripe_customer_id
├── stripe_subscription_id
├── status (active, trialing, past_due, canceled, unpaid)
├── current_period_end
├── created_at
├── updated_at
└── is_active() method
```

#### Protected Routes

- Login Required: `/` (home), `/pro/`, `/billing/`
- Pro Feature Gated: `/pro/` (via `@require_pro` decorator)
- Public: `/login/`, `/pricing/`, `/health/`

### Request/Response Flow

#### Authentication Flow

```
1. User navigates to /login/
2. POST credentials to Django login endpoint
3. Django creates session (stores in cache/DB)
4. Redirect to dashboard with session cookie
5. All subsequent requests include session cookie
6. ProMiddleware checks subscription status
7. Render appropriate dashboard (free vs pro)
```

#### API Request Flow

```
1. Frontend (React) makes HTTP request
2. CORS middleware checks origin
3. CSRF middleware validates token
4. Authentication middleware checks session
5. View decorator checks authorization
6. View processes request
7. Database query with ORM
8. Response serialized to JSON
9. Security headers added
10. Response sent to frontend
```

### Middleware Stack (Order Matters)

```
1. SecurityMiddleware         # SSL redirect, security headers
2. WhiteNoiseMiddleware       # Static file serving
3. HTTPSRedirectMiddleware    # Force HTTPS (custom)
4. SecurityHeadersMiddleware  # XSS, clickjacking headers (custom)
5. CorsMiddleware             # CORS configuration
6. SessionMiddleware          # Session management
7. CommonMiddleware           # Common utilities
8. CsrfViewMiddleware         # CSRF protection
9. AuthenticationMiddleware   # User authentication
10. MessageMiddleware         # Django messages
11. ClickjackingMiddleware    # X-Frame-Options
12. ProMiddleware             # Pro feature access (custom)
```

---

## FRONTEND ARCHITECTURE

### Project Structure

```
frontend/
├── public/
│   └── index.html           # Entry point
├── src/
│   ├── index.js             # React entry
│   ├── App.js               # Root component
│   ├── api.js               # API client (Axios/Fetch)
│   ├── auth.js              # Authentication logic
│   ├── theme.css            # Global styles
│   ├── components/
│   │   ├── LoginForm.js
│   │   ├── Dashboard.js
│   │   ├── Pricing.js
│   │   ├── ProFeature.js
│   │   └── Navigation.js
│   ├── pages/
│   │   ├── HomePage.js
│   │   ├── DashboardPage.js
│   │   ├── PricingPage.js
│   │   └── ProPage.js
│   ├── context/
│   │   ├── AuthContext.js   # Auth state management
│   │   └── SubscriptionContext.js
│   ├── hooks/
│   │   ├── useAuth.js
│   │   └── useSubscription.js
│   ├── theme/
│   │   ├── colors.js
│   │   └── typography.js
│   └── __tests__/           # Jest tests
├── package.json
├── jest.config.json
└── .env.local               # Environment variables
```

### API Client (api.js)

```javascript
// Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api'

// Common endpoints
- GET  /api/profile/               # Get current user profile
- POST /api/login/                 # Login
- POST /api/logout/                # Logout
- GET  /api/billing/status/        # Get subscription status
- POST /api/billing/checkout/      # Create Stripe checkout session
- GET  /api/stripe/portal/         # Stripe customer portal redirect
```

### Authentication Flow (Frontend)

```
1. User enters email/password on login form
2. POST request to /api/login/
3. Backend sets session cookie (httponly)
4. Frontend stores user in AuthContext
5. Redirect to dashboard
6. On page refresh:
   - GET /api/profile/ to verify session
   - Restore user from response
   - If 401, redirect to login
```

### State Management

```javascript
// AuthContext provides:
-currentUser -
  isAuthenticated -
  login(email, password) -
  logout() -
  setUser(user) -
  // SubscriptionContext provides:
  subscription -
  isPro -
  isActive -
  refreshSubscription();
```

---

## DATABASE DESIGN

### Entity Relationship Diagram

```
User
├── (extends Django User)
├── username
├── email
├── password_hash
└── profile (1:1) ──→ Profile
                      ├── is_subscribed
                      ├── trial_end_date
                      └── subscription (1:1) ──→ Subscription
                                                  ├── stripe_customer_id
                                                  ├── stripe_subscription_id
                                                  ├── status
                                                  └── current_period_end

WebhookEvent
├── event_id (unique, indexed)
├── event_type (indexed)
├── processed (indexed)
├── processed_at
├── error_message
├── event_hash
├── created_at (indexed)
└── updated_at
```

### Critical Indexes

```sql
-- Subscription queries (fast status checks)
CREATE INDEX idx_subscription_status ON billing_subscription(status);

-- Webhook idempotency (fast duplicate detection)
CREATE INDEX idx_webhook_event_id ON billing_webhookevent(event_id);
CREATE INDEX idx_webhook_event_type_processed
  ON billing_webhookevent(event_type, processed);

-- User lookups (fast authentication)
CREATE INDEX idx_user_email ON auth_user(email);
```

### Database Migrations

```
All migrations use Django's migration framework:
- users/migrations/0001_initial.py
- billing/migrations/0001_initial.py
- billing/migrations/0002_*.py

Run with: python manage.py migrate
Rollback with: python manage.py migrate billing 0001
```

### Connection Pooling

```python
# Production settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

---

## API ARCHITECTURE

### RESTful Endpoints

#### Authentication

```
POST   /api/login/              # Session-based login
POST   /api/logout/             # Clear session
GET    /api/profile/            # Get current user
POST   /api/register/           # Create account
POST   /api/password-reset/     # Initiate reset
```

#### Billing

```
GET    /api/billing/status/     # Get subscription status
POST   /api/billing/checkout/   # Create checkout session
GET    /api/stripe/portal/      # Redirect to Stripe portal
GET    /api/invoices/           # List user invoices
```

#### AI Features (Pro only)

```
POST   /api/ai/generate/        # Generate AI content
GET    /api/ai/history/         # User's AI requests
```

#### Health & Status

```
GET    /health/                 # Health check endpoint
```

### Request/Response Format

#### Successful Response (200-201)

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "subscription": {
        "status": "active",
        "current_period_end": "2026-02-15"
      }
    }
  }
}
```

#### Error Response (400-500)

```json
{
  "success": false,
  "error": "Subscription inactive",
  "code": "SUBSCRIPTION_INACTIVE",
  "status": 403
}
```

### CORS Configuration

```python
# Production
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]

# Development
CORS_ALLOW_ALL_ORIGINS = True  # When DEBUG=True
```

### Rate Limiting

```
Global: 1000 requests/minute per IP
Webhooks: 100 events/minute (Stripe retry compatible)
Login: 5 attempts/15 minutes per email
API: 100 requests/minute per authenticated user
```

---

## SECURITY ARCHITECTURE

### Security Layers

#### 1. Transport Security

```
- HTTPS only (SSL/TLS)
- HSTS headers (1 year)
- Certificate pinning (optional)
```

#### 2. Authentication

```
- Session-based (Django)
- HTTPOnly cookies
- SameSite=Lax
- CSRF tokens on all mutations
```

#### 3. Authorization

```
- @login_required decorator
- @require_pro decorator
- Subscription status checks
- Object-level permission validation
```

#### 4. Data Protection

```
- Password hashing (PBKDF2)
- Stripe PCI DSS Level 1
- Encrypted database connections
- No PII in logs (send_default_pii=False for Sentry)
```

#### 5. Input Validation

```
- Django form validation
- DRF serializer validation
- CSRF token validation
- Webhook signature verification
```

#### 6. Output Encoding

```
- HTML auto-escaping
- JSON encoding
- SQL parameterization (ORM)
```

### Secret Management

```
Environment Variable                Location
DJANGO_SECRET_KEY        →  .env (production)
STRIPE_SECRET_KEY        →  .env (production)
STRIPE_WEBHOOK_SECRET    →  .env (production)
DATABASE_URL             →  .env (production)
ALLOWED_HOSTS            →  .env (production)
CSRF_TRUSTED_ORIGINS     →  .env (production)
```

### Webhook Security

```
1. Stripe sends webhook with timestamp + signature
2. Extract signature from HTTP_STRIPE_SIGNATURE header
3. Reconstruct signature using webhook secret
4. Compare signatures (constant-time comparison)
5. If valid, process event
6. Check WebhookEvent for idempotency (event_id unique)
7. Store processed status to prevent duplicates
```

---

## DEPLOYMENT ARCHITECTURE

### Docker Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
services:
  backend:
    build: ./backend
    ports: [8000:8000]
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.settings
    depends_on: [db, redis]

  frontend:
    build: ./frontend
    ports: [3000:3000]
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password

  redis:
    image: redis:7-alpine
```

### Production Deployment

#### Render.com

```yaml
# render.yaml
services:
  - type: web
    name: saas-backend
    runtime: python
    buildCommand: pip install -r requirements.txt && python manage.py migrate
    startCommand: gunicorn config.wsgi:application
    envVars:
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: yourdomain.com
```

#### AWS EC2 + RDS

```
1. Launch EC2 instance (t3.medium, Ubuntu 22.04)
2. Install Docker & Docker Compose
3. Create RDS PostgreSQL database
4. Create ElastiCache Redis cluster
5. Configure security groups
6. Deploy Docker Compose stack
7. Set up CloudFront CDN
8. Configure Route53 DNS
```

#### Nginx Reverse Proxy

```nginx
upstream django {
    server backend:8000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## SCALING & PERFORMANCE

### Horizontal Scaling

```
1. Stateless backend (no local caching)
2. Shared session store (Redis)
3. Shared database (PostgreSQL with replicas)
4. Load balancer (AWS ELB, Nginx)
5. Scale to 5-100 backend instances
```

### Database Performance

```
1. Connection pooling (conn_max_age=600)
2. Query optimization (select_related)
3. Database indexing (event_id, status)
4. Read replicas for reporting
5. Caching layer (Redis)
```

### Caching Strategy

```
Layer 1: Browser cache (static files, 1 year)
Layer 2: Cloudflare cache (HTML, 5 minutes)
Layer 3: Redis cache (API responses, 5 minutes)
Layer 4: Database cache (query cache, Django ORM)
```

### Performance Metrics

```
Target Metrics:
- Page load: < 2 seconds
- API response: < 200ms (p95)
- Database query: < 100ms (p95)
- Webhook processing: < 1 second
- Uptime: > 99.95%

Monitoring:
- Sentry error tracking
- New Relic APM
- Custom metrics in logs
- Health check endpoint
```

### CDN Integration (Cloudflare)

```
- Static assets: Cache 1 year
- HTML pages: Cache 5 minutes
- API endpoints: No cache (but compress)
- Images: Cache 1 month
- Minification: Enabled
- Compression: gzip + brotli
```

---

## CONCLUSION

This architecture is designed to:

- ✅ Scale horizontally (add more servers)
- ✅ Provide security (HTTPS, CSRF, rate limiting)
- ✅ Ensure reliability (error tracking, monitoring)
- ✅ Maintain data integrity (transactions, indexing)
- ✅ Support growth (caching, CDN, database replicas)

All components are production-ready and follow industry best practices.

---

_Document: Technical Architecture | Version: 1.0 | Status: APPROVED ✅_
