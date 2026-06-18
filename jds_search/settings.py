import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "jds-search-secret-key-change-in-production")

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

BASE_DOMAIN = os.environ.get("BASE_DOMAIN", "jds-search.de")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".lvh.me", ".jds-search.de", "*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "search",
    "jdai",
    "mail_app",
    "planner",
    "marketplace",
    "insights",
    "present",
    "notes",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "core.middleware.SubdomainRoutingMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jds_search.urls"

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
                "core.context_processors.jds_domain",
            ],
        },
    },
]

WSGI_APPLICATION = "jds_search.wsgi.application"

USE_SUPABASE = os.environ.get("USE_SUPABASE", "True").lower() in ("true", "1", "yes")

if USE_SUPABASE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres.bdbhxdpvxevvlzsygabq",
            "PASSWORD": "J2E8L0JDS2025!",
            "HOST": "aws-0-eu-west-1.pooler.supabase.com",
            "PORT": "6543",
            "OPTIONS": {"sslmode": "require"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = []

# Email SMTP - Fur Entwicklung: Console-Backend, Produktion: SMTP
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@jds-search.de")

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/search/"
LOGOUT_REDIRECT_URL = "/"

if not DEBUG:
    CSRF_COOKIE_DOMAIN = ".jds-search.de"
    SESSION_COOKIE_DOMAIN = ".jds-search.de"

CSRF_TRUSTED_ORIGINS = [
    "https://*.jds-search.de", "https://jds-search.de",
    "http://*.lvh.me", "http://lvh.me",
    "http://localhost:8000", "http://127.0.0.1:8000",
]
