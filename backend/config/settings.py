"""
Django settings for the SkillSwap project.

Configuration is 12-factor style: all environment-specific values are read
from environment variables (optionally loaded from the project-root .env file
via python-dotenv). The same settings module is used for local development and
production; behavior switches on the DEBUG flag and companion variables.

Architecture note (see docs/ARCHITECTURE.md):
We deliberately keep a single settings module instead of base/local/prod
splits. This reduces import-order pitfalls and duplicate settings while
remaining production safe because every sensitive value is pulled from the
environment.
"""

from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the project root (.env is ignored by git).
ENV_FILE = BASE_DIR.parent / '.env'
load_dotenv(ENV_FILE)

import os  # noqa: E402


def _env(key: str, default: str = '') -> str:
    """Read a string value from the environment."""
    return os.environ.get(key, default)


def _env_bool(key: str, default: bool) -> bool:
    """Parse a boolean environment variable."""
    raw = os.environ.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in {'1', 'true', 'yes', 'on'}


def _env_int(key: str, default: int) -> int:
    """Parse an integer environment variable."""
    raw = os.environ.get(key)
    if raw is None or raw.strip() == '':
        return default
    return int(raw)


def _env_list(key: str, default: list[str] | None = None) -> list[str]:
    """Parse a comma-separated list environment variable."""
    raw = os.environ.get(key)
    if raw is None or raw.strip() == '':
        return default or []
    return [item.strip() for item in raw.split(',') if item.strip()]


# DJANGO_SECRET_KEY is required in production; a dev-only fallback is allowed
# strictly for local development.
SECRET_KEY = _env('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    SECRET_KEY = 'dev-only-insecure-secret-key-change-in-production'

DEBUG = _env_bool('DEBUG', default=True)

_ALLOWED_HOSTS = _env_list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
ALLOWED_HOSTS = ['*'] if DEBUG else _ALLOWED_HOSTS

if not DEBUG and SECRET_KEY == 'dev-only-insecure-secret-key-change-in-production':
    raise RuntimeError('DJANGO_SECRET_KEY must be set to a strong value in production.')

# --------------------------------------------------------------------------
# Application definition
# --------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'corsheaders',
    # Local apps
    'apps.core',
    'apps.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _env('DATABASE_NAME', 'skillswap_db'),
        'USER': _env('DATABASE_USER', 'postgres'),
        'PASSWORD': _env('DATABASE_PASSWORD', ''),
        'HOST': _env('DATABASE_HOST', 'localhost'),
        'PORT': _env('DATABASE_PORT', '5432'),
        # Reuse connections per worker; dramatically reduces handshake cost.
        'CONN_MAX_AGE': _env_int('DATABASE_CONN_MAX_AGE', 60),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------------------------------
# Django REST Framework
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Secure by default: endpoints require authentication unless explicitly
    # allowed (e.g. registration, login, public listing search).
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
}

# JWT configuration. When JWT_SECRET_KEY is empty the Django SECRET_KEY is
# reused so tokens are always signed with a strong, non-empty key.
_JWT_SIGNING_KEY = _env('JWT_SECRET_KEY') or SECRET_KEY

from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=_env_int('JWT_ACCESS_TOKEN_MINUTES', 30)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=_env_int('JWT_REFRESH_TOKEN_DAYS', 30)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'SIGNING_KEY': _JWT_SIGNING_KEY,
}

# --------------------------------------------------------------------------
# CORS
# --------------------------------------------------------------------------

_CORS_ORIGINS = _env_list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:5173', 'http://127.0.0.1:5173'],
)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = _CORS_ORIGINS
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = _CORS_ORIGINS

CORS_ALLOW_CREDENTIALS = True

# --------------------------------------------------------------------------
# Password validation
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.User'

# --------------------------------------------------------------------------
# Internationalization
# --------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static files and media
# --------------------------------------------------------------------------

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --------------------------------------------------------------------------
# Email
#
# Django 6 moved email configuration to the MAILERS framework
# (EMAIL_BACKEND and friends are deprecated and removed in Django 7).
# See: https://docs.djangoproject.com/en/6.1/topics/email/#mailers
# --------------------------------------------------------------------------

_DEFAULT_FROM_EMAIL = _env('DEFAULT_FROM_EMAIL', 'SkillSwap <no-reply@skillswap.local>')
DEFAULT_FROM_EMAIL = _DEFAULT_FROM_EMAIL

_EMAIL_BACKEND = _env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend',
)

_MAILERS_DEFAULT: dict = {'BACKEND': _EMAIL_BACKEND}

if _EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    _MAILERS_DEFAULT['OPTIONS'] = {
        'host': _env('EMAIL_HOST'),
        'port': _env_int('EMAIL_PORT', 587),
        'username': _env('EMAIL_HOST_USER'),
        'password': _env('EMAIL_HOST_PASSWORD'),
        'use_tls': _env_bool('EMAIL_USE_TLS', True),
    }

MAILERS = {'default': _MAILERS_DEFAULT}

# --------------------------------------------------------------------------
# Security
# --------------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = _env_list('CSRF_TRUSTED_ORIGINS') or list(_CORS_ORIGINS)

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = _env_bool('SECURE_SSL_REDIRECT', True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '{levelname} {asctime} {name} {module} {process:d} {thread:d} {message}'
            ),
            'style': '{',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django.server': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}
