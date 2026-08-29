import os
from pathlib import Path
from datetime import timedelta

import dj_database_url

# Detect Vercel serverless environment
# Vercel automatically sets the VERCEL env var to "1" during builds and at runtime.
IS_VERCEL = os.environ.get("VERCEL", "") == "1"

# ──────────────────────────────────────────────
# BASE DIRECTORY
# ──────────────────────────────────────────────
# Points to: expense-manager/backend/
BASE_DIR = Path(__file__).resolve().parent.parent


# ──────────────────────────────────────────────
# SECURITY SETTINGS
# ──────────────────────────────────────────────

# SECRET_KEY: Used for cryptographic signing (sessions, tokens, etc.)
# In production, this MUST be set as an environment variable.
# The fallback value is ONLY for local development.
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-qik%vjxsvo$(zrrckdl)o=6&k$iwryc)zg)uan0bef05opq8^g",
)

# DEBUG: Shows detailed error pages. Must be False in production!
# On Render/Railway, set env var DEBUG=False.
# Defaults to True for local development convenience.
DEBUG = os.environ.get("DEBUG", "True") == "True"

# ALLOWED_HOSTS: Which domains can serve this app.
# In production, set env var ALLOWED_HOSTS=your-app.onrender.com
# In development with DEBUG=True, Django allows localhost automatically.
ALLOWED_HOSTS = list(filter(None, os.environ.get("ALLOWED_HOSTS", "").split(",")))

# Vercel serverless: always allow .vercel.app domains and localhost
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]  # Fallback — tighten via env var in production


# ──────────────────────────────────────────────
# INSTALLED APPS
# ──────────────────────────────────────────────
INSTALLED_APPS = [
    # Django built-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",               # Django REST Framework (API)
    "rest_framework_simplejwt",      # JWT Authentication
    "corsheaders",                   # Cross-Origin Resource Sharing

    # Your apps
    "expenses",                      # Expense Manager app
]


# ──────────────────────────────────────────────
# MIDDLEWARE
# ──────────────────────────────────────────────
# Order matters! Each request passes through these top-to-bottom.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # Serves static files in production (must be right after SecurityMiddleware)

    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",         # Must be before CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ──────────────────────────────────────────────
# URL & WSGI CONFIGURATION
# ──────────────────────────────────────────────
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"


# ──────────────────────────────────────────────
# TEMPLATES
# ──────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ──────────────────────────────────────────────
# DATABASE
# ──────────────────────────────────────────────
# dj_database_url reads the DATABASE_URL environment variable automatically.
#
# On Render:
#   1. Create a PostgreSQL database (free tier)
#   2. Copy the "Internal Database URL"
#   3. Add it as env var: DATABASE_URL=postgres://user:pass@host:5432/dbname
#
# Locally (no DATABASE_URL set):
#   Falls back to SQLite for easy development.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        # conn_max_age=0 on Vercel: serverless functions are stateless,
        # persistent connections cause errors between invocations.
        conn_max_age=0,
        conn_health_checks=False,
    )
}


# ──────────────────────────────────────────────
# PASSWORD VALIDATION
# ──────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ──────────────────────────────────────────────
# INTERNATIONALIZATION
# ──────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ──────────────────────────────────────────────
# STATIC FILES (CSS, JavaScript, Images)
# ──────────────────────────────────────────────
# URL prefix for static files
STATIC_URL = "/static/"

# Directory where `collectstatic` gathers all static files for production.
# On Vercel, the lambda filesystem is read-only except /tmp.
if IS_VERCEL:
    STATIC_ROOT = "/tmp/staticfiles"
else:
    STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise compresses & caches static files for fast serving.
# Use CompressedStaticFilesStorage (not Manifest variant) to avoid
# "Missing staticfiles manifest" errors on Vercel cold starts.
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# ──────────────────────────────────────────────
# CORS (Cross-Origin Resource Sharing)
# ──────────────────────────────────────────────
# Allows your React frontend (on a different domain) to call this API.
#
# In production, set env var:
#   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com
#
# In development (DEBUG=True), all origins are allowed automatically.
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = list(
        filter(None, os.environ.get("CORS_ALLOWED_ORIGINS", "").split(","))
    )

# Explicitly allow common headers including Authorization (for JWT)
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# CSRF trusted origins for cross-origin POST requests (if needed)
CSRF_TRUSTED_ORIGINS = list(
    filter(None, os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(","))
)


# ──────────────────────────────────────────────
# DEFAULT PRIMARY KEY TYPE
# ──────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ──────────────────────────────────────────────
# DJANGO REST FRAMEWORK
# ──────────────────────────────────────────────
# All API endpoints require a valid JWT token by default.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}


# ──────────────────────────────────────────────
# JWT (JSON Web Token) SETTINGS
# ──────────────────────────────────────────────
# Access token: used to authenticate API requests (valid 7 days)
# Refresh token: used to get a new access token (valid 30 days)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}


# ──────────────────────────────────────────────
# PRODUCTION SECURITY SETTINGS
# ──────────────────────────────────────────────
# These settings are enabled only in production (DEBUG=False).
# They enforce HTTPS, secure cookies, and HSTS.
if not DEBUG:
    # Vercel terminates SSL at the edge and forwards requests as HTTP internally.
    # SECURE_SSL_REDIRECT=True would cause infinite redirect loops on Vercel.
    # Default is False; set env var SECURE_SSL_REDIRECT=True only on non-Vercel hosts.
    SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False") == "True"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")