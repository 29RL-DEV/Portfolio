from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize Sentry for error tracking (optional but recommended for production)
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1 if not os.getenv("DEBUG") == "True" else 0.5,
        send_default_pii=False,  # Don't send PII to Sentry
    )


# ============================
# CORE
# ============================

# SECRET_KEY is REQUIRED in production - fail if not set
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("DEBUG", "True") == "True":
        SECRET_KEY = "dev-secret-key-change-in-production"
    else:
        raise ValueError("SECRET_KEY environment variable must be set in production!")

DEBUG = os.getenv("DEBUG") == "True"





# PRODUCTION VALIDATION
if not DEBUG:
    # Ensure SECRET_KEY is not the default dev key in production
    if SECRET_KEY == "dev-secret-key-change-in-production":
        raise ValueError(
            "CRITICAL: Default SECRET_KEY used in production! Set SECRET_KEY environment variable."
        )

    # Ensure domain is configured in production
    if not os.getenv("ALLOWED_HOSTS"):
        raise ValueError("CRITICAL: ALLOWED_HOSTS must be set in production!")

ALLOWED_HOSTS_ENV = os.getenv("ALLOWED_HOSTS")

if not ALLOWED_HOSTS_ENV:
    if DEBUG:
        ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
    else:
        raise ValueError("ALLOWED_HOSTS must be set in production")
else:
    ALLOWED_HOSTS = ALLOWED_HOSTS_ENV.split(",")

# CSRF_TRUSTED_ORIGINS - configurable via environment variable
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")


# ============================
# AUTH
# ============================

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


# ============================
# APPS
# ============================

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "rest_framework",
    "django_ratelimit",
    "users",
    "billing",
    "api",
    "core",
]


# ============================
# MIDDLEWARE
# ============================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Auto-redirect HTTPS to HTTP in development (prevents HTTPS errors)
    "config.middleware.HTTPSRedirectMiddleware",
    # Security headers (XSS, clickjacking, MIME sniffing protection)
    "config.middleware.SecurityHeadersMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "api.views.ProMiddleware",
]


ROOT_URLCONF = "config.urls"

# Error handlers
handler404 = "config.views.handler404"
handler500 = "config.views.handler500"
handler403 = "config.views.handler403"
handler400 = "config.views.handler400"


# ============================
# TEMPLATES
# ============================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# ============================
# DATABASE
# ============================

import dj_database_url

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ============================
# PASSWORDS
# ============================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ============================
# I18N
# ============================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ============================
# STATIC FILES
# ============================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================
# LOGGING
# ============================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": ["suppress_https_errors"] if DEBUG else [],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": (
                "WARNING" if DEBUG else "INFO"
            ),  # Reduce HTTPS error noise in development
            "propagate": False,
        },
        "billing": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "config": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
    "filters": {
        "suppress_https_errors": {
            "()": "config.logging_filters.SuppressHTTPSErrorsFilter",
        },
    },
}


# ============================
# SECURITY
# ============================

SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # CSRF token must be readable by JS
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
else:
    SECURE_HSTS_SECONDS = 0
    SECURE_PROXY_SSL_HEADER = None


# ============================
# CORS
# ============================

# CORS configuration - restrict in production!
CORS_ALLOW_ALL_ORIGINS = False if not DEBUG else True


if not CORS_ALLOW_ALL_ORIGINS:
    # Allow specific origins from environment variable
    CORS_ALLOWED_ORIGINS = os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")


# ============================
# STRIPE
# ============================

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")

# OpenAI (optional - for AI features)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# ============================
# SENTRY (OPTIONAL)
# ============================

SENTRY_DSN = os.getenv("SENTRY_DSN")

if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=0.1,
        )
    except Exception:
        pass


# ============================
# EMAIL CONFIGURATION
# ============================

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@yourdomain.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL


# ============================
# CACHING (REDIS)
# ============================

REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "saas",
            "TIMEOUT": 300,
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    # For development without Redis: Use local memory cache
    # This works fine for single-process development
    # For production: Use Redis (set REDIS_URL) for proper shared cache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }


# ============================
# DJANGO RATELIMIT CONFIGURATION
# ============================

RATELIMIT_USE_CACHE = "default"

# Silence django_ratelimit warnings for LocMemCache in development
# The cache backend works fine for single-process development, though it's not ideal for production
SILENCED_SYSTEM_CHECKS = ["django_ratelimit.E003", "django_ratelimit.W001"]

# For development: Rate limiting will work with LocMemCache in single-process mode
# This is acceptable for local development and testing
# For production: Use Redis (set REDIS_URL) for proper shared cache support


# ============================
# AWS S3 (OPTIONAL)
# ============================

if os.getenv("AWS_STORAGE_BUCKET_NAME"):
    INSTALLED_APPS.append("storages")

    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
