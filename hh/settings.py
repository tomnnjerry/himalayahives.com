"""Django settings for himalayahives.com."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,himalayahives.com,www.himalayahives.com").split(",")
CSRF_TRUSTED_ORIGINS = ["https://himalayahives.com", "https://www.himalayahives.com"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "hives",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

try:  # optional: serves /static/ efficiently in production
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
except ImportError:
    pass

ROOT_URLCONF = "hh.urls"
WSGI_APPLICATION = "hh.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "hives.context.site",
    ]},
}]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = False
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CONTENT_DIR = BASE_DIR / "content"

# Business details. Fill these before launch; placeholders render as-is.
SITE = {
    "name": "Himalaya Hives",
    "tagline": "Every valley is a hive",
    "url": "https://himalayahives.com",
    "email": os.environ.get("HH_EMAIL", "[YOUR EMAIL]"),
    "phone": os.environ.get("HH_PHONE", "[YOUR PHONE]"),
    "whatsapp": os.environ.get("HH_WHATSAPP", ""),  # digits with country code, e.g. 919800000000
    "address": "[YOUR OFFICE ADDRESS]",
    "byline": "Himalaya Hives Field Desk",
}

# Optional Google Analytics 4 measurement ID (e.g. G-XXXXXXX). Leave empty to load no analytics.
GA4_ID = os.environ.get("HH_GA4", "")

# Production: hashed file names so every deploy busts browser caches.
# Set HH_HASHED_STATIC=1 on the server AFTER `python manage.py collectstatic`.
if os.environ.get("HH_HASHED_STATIC") == "1":
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
                        if "whitenoise.middleware.WhiteNoiseMiddleware" in MIDDLEWARE
                        else "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
    }

# Production security. Set HH_HTTPS=1 on the server once TLS is in place.
if os.environ.get("HH_HTTPS") == "1":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Email alerts for new enquiries (optional). Set HH_NOTIFY_EMAIL and the SMTP variables to receive them.
EMAIL_HOST = os.environ.get("HH_SMTP_HOST", "")
EMAIL_PORT = int(os.environ.get("HH_SMTP_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("HH_SMTP_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("HH_SMTP_PASSWORD", "")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get("HH_FROM_EMAIL", "Himalaya Hives <no-reply@himalayahives.com>")
HH_NOTIFY_EMAIL = os.environ.get("HH_NOTIFY_EMAIL", "")
if not EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
