import os
from pathlib import Path
from datetime import timedelta

import dj_database_url


# ============================================================
# BASE DIRECTORY & ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env file natively if it exists (no external package required)
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    with open(_env_file, encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip("'\""))


# ============================================================
# ENVIRONMENT
# ============================================================

ENVIRONMENT = os.environ.get("ENVIRONMENT", "local").lower()

DEBUG = (
    os.environ.get(
        "DEBUG",
        "True" if ENVIRONMENT == "local" else "False",
    ).lower()
    == "true"
)


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-development-only-change-this",
)


# ============================================================
# ALLOWED HOSTS
# ============================================================

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".vercel.app",
]

extra_hosts = os.environ.get("ALLOWED_HOSTS", "")

if extra_hosts:
    ALLOWED_HOSTS.extend(
        host.strip()
        for host in extra_hosts.split(",")
        if host.strip()
    )


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",

    # Local apps
    "expenses",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # Sessions
    "django.contrib.sessions.middleware.SessionMiddleware",

    # CORS
    # IMPORTANT:
    # CORS middleware must be before CommonMiddleware.
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.common.CommonMiddleware",

    # CSRF
    "django.middleware.csrf.CsrfViewMiddleware",

    # Authentication
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # Messages
    "django.contrib.messages.middleware.MessageMiddleware",

    # Security
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL / WSGI
# ============================================================

ROOT_URLCONF = "core.urls"

WSGI_APPLICATION = "core.wsgi.application"


# ============================================================
# TEMPLATES
# ============================================================

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


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:

    db_config = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=0,
        conn_health_checks=False,
    )
    db_config.setdefault("OPTIONS", {})
    db_config["OPTIONS"].setdefault("connect_timeout", 10)

    DATABASES = {
        "default": db_config
    }

else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]


# ============================================================
# AUTHENTICATION BACKENDS
# ============================================================

AUTHENTICATION_BACKENDS = [
    "expenses.backends.CaseInsensitiveEmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedStaticFilesStorage"
        ),
    },
}


# ============================================================
# CORS
# ============================================================

# ------------------------------------------------------------
# Local React / Vite frontend
# ------------------------------------------------------------

LOCAL_FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


# ------------------------------------------------------------
# Production frontend origins
# ------------------------------------------------------------

ENV_CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "",
    ).split(",")
    if origin.strip()
]


# ------------------------------------------------------------
# Final allowed CORS origins
# ------------------------------------------------------------

CORS_ALLOWED_ORIGINS = list(
    dict.fromkeys(
        LOCAL_FRONTEND_ORIGINS
        + ENV_CORS_ORIGINS
    )
)

# Automatically allow all Vercel deployed frontend origins
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True


# ============================================================
# CORS CREDENTIALS
# ============================================================

# You are using JWT authentication.
#
# JWT is normally sent using:
#
# Authorization: Bearer <token>
#
# Therefore keep this False unless you specifically
# start using authentication cookies.

CORS_ALLOW_CREDENTIALS = False


# ============================================================
# CORS HEADERS
# ============================================================

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


# ============================================================
# CORS METHODS
# ============================================================

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "",
    ).split(",")
    if origin.strip()
]


# Add local frontend automatically
for origin in LOCAL_FRONTEND_ORIGINS:

    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

}


# ============================================================
# JWT
# ============================================================

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(
        days=7
    ),

    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=30
    ),

}


# ============================================================
# PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    # --------------------------------------------------------
    # HTTPS Redirect
    # --------------------------------------------------------

    SECURE_SSL_REDIRECT = (
        os.environ.get(
            "SECURE_SSL_REDIRECT",
            "False",
        ).lower()
        == "true"
    )


    # --------------------------------------------------------
    # Secure Cookies
    # --------------------------------------------------------

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True


    # --------------------------------------------------------
    # HSTS
    # --------------------------------------------------------

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True


    # --------------------------------------------------------
    # Vercel / Proxy HTTPS
    # --------------------------------------------------------

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )