"""
Base settings to build other settings files upon.
"""

import os
import socket
import datetime
import environ
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


def get_env_var(var_name, default=None):
    var = os.getenv(var_name, default)
    if var is None and default is None:
        raise ImproperlyConfigured(f'Set the {var_name} environment variable')
    return var


def get_int_env_var(var_name, default=None):
    var = get_env_var(var_name, default)
    try:
        return int(var)
    except ValueError:
        raise ImproperlyConfigured(f'Environment variable {var_name} '
                                   f'must be an integer or integer-convertible string')


def split_env_var(var_name, sep=','):
    var = get_env_var(var_name, '')
    return [e.strip() for e in var.split(sep)]


# ROOT_DIR = ozone/config/settings/base.py - 3 = ozone/
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = ROOT_DIR / 'ozone' 

env = environ.Env()

READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR / '.env' ))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = 'Africa/Nairobi'
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.get_value('POSTGRES_DB', default=""),
        'HOST': env.get_value('POSTGRES_HOST', default=""),
        'USER': env.get_value('POSTGRES_USER', default=""),
        'PASSWORD': env.get_value('POSTGRES_PASSWORD', default=""),
    }
}
DATABASES['default']['ATOMIC_REQUESTS'] = True

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'config.urls'
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.humanize', # Handy template tags
    # 'django.contrib.admin', # Replaced by OzoneAdminConfig
]
THIRD_PARTY_APPS = [
    'corsheaders',
    'crispy_forms',
    'rest_framework',
    'rest_framework.authtoken',
    'webpack_loader',
    'guardian',
    'django_filters',
    'simple_history',
    'oauth2_provider',
    'django_admin_listfilter_dropdown',
    'adminactions',
]
LOCAL_APPS = [
    # Your stuff: custom apps go here
    'ozone.core.apps.CoreConfig',
    'ozone.core.apps.OzoneAdminConfig',
    'impersonate',
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = THIRD_PARTY_APPS + LOCAL_APPS + DJANGO_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {
    'sites': 'ozone.contrib.sites.migrations'
}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]

TOKEN_EXPIRE_INTERVAL = datetime.timedelta(days=get_int_env_var('TOKEN_EXPIRE_INTERVAL',
                                                                default=30))

CORS_ALLOW_CREDENTIALS = True
OZONE_HOST = env('OZONE_HOST', default="")
CORS_ORIGIN_WHITELIST = ()
if OZONE_HOST:
    CORS_ORIGIN_WHITELIST = (
        OZONE_HOST,
    )

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = 'core.User'
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = 'admin:login'

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'ozone.core.middleware.TokenAdminAuthMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'ozone.core.middleware.ExceptionMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'ozone.core.middleware.ImpersonateTokenAuthMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = ROOT_DIR / 'static'
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    ROOT_DIR / 'ozone' / 'static',
)

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/local/media'

FILE_UPLOAD_PERMISSIONS = 0o644

# TODO: this part should be synchronized with Webpack
# (see /frontend/config/conf.js)
_WEBPACK_DIST_DIR = ROOT_DIR / 'frontend' / 'dist'

# TODO: enable this only in production. (this is just a hack
# because the staticfiles app breaks if the directory doesn't exist.)

if _WEBPACK_DIST_DIR.is_dir():
    STATICFILES_DIRS = (
        *STATICFILES_DIRS,
        _WEBPACK_DIST_DIR,
    )



# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            ROOT_DIR / 'templates', APPS_DIR / 'templates',
        ],
        'OPTIONS': {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            # 'debug': DEBUG,
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
# CRISPY_TEMPLATE_PACK = 'bootstrap4'


# Security
CSRF_FAILURE_VIEW = 'ozone.core.views.csrf_failure'


# Guardian
ANONYMOUS_USER_NAME = None


# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'ozone.core.utils.api.BrowsableAPIRendererWithoutForms',
    ),
    'COERCE_DECIMAL_TO_STRING': False,
}


# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (
    str(ROOT_DIR / 'data' / 'fixtures'),
)

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = 'smtp'
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 25
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = 'user'
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = 'pwd'
# https://docs.djangoproject.com/en/2.1/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = 'no-reply@%s' % socket.gethostname()

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = 'admin/'
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ("""Sorin Stelian""", 'sorin.stelian@eaudeweb.ro'),
]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS


# Your stuff...
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# https://django-oauth-toolkit.readthedocs.io/en/latest/settings.html
OAUTH2_PROVIDER = {
    # https://django-oauth-toolkit.readthedocs.io/en/latest/settings.html#scopes
    'SCOPES': {
        'read': 'Read scope',
    },
    # https://django-oauth-toolkit.readthedocs.io/en/latest/settings.html#request-approval-prompt
    # Set to auto instead of "force" to remember if the application was previously
    # authorized or not.
    "REQUEST_APPROVAL_PROMPT": 'auto',
}

# Tusd settings
TUSD_UPLOADS_DIR = env('TUSD_UPLOADS_DIR', default='/var/local/tusd_uploads')
TUSD_HOST = env('TUSD_HOST', default='localhost')
TUSD_PORT = env('TUSD_PORT', default='1080')
ALLOWED_FILE_EXTENSIONS = split_env_var('ALLOWED_FILE_EXTENSIONS')

# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [
    ROOT_DIR / 'translations' / 'backend',
]

USE_I18N = True
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('ar', 'العربية'),
    ('zh', '中文'),
    ('en', 'English'),
    ('fr', 'Français'),
    ('ru', 'Русский'),
    ('es', 'Español'),
)

SENTRY_DSN = env('SENTRY_DSN', default=None)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        release=env('SENTRY_RELEASE', default='dev'),
        environment=env('SENTRY_ENV', default=''),
        integrations=[DjangoIntegration()]
    )

# Impersonate
IMPERSONATE = {
    'REQUIRE_SUPERUSER': True,
    'REDIRECT_URL': '/',
}

# Cache invalidation
# No cache invalidation will be attempted by default if host/port not given
CACHE_INVALIDATION_URL = env('CACHE_INVALIDATION_URL', default=None)
# Timeout is in seconds
CACHE_INVALIDATION_TIMEOUT=env('CACHE_INVALIDATION_TIMEOUT', default=1)
# Authentication for cache invalidation (basic by default)
CACHE_INVALIDATION_USER=env('CACHE_INVALIDATION_USER', default='')
CACHE_INVALIDATION_PASS=env('CACHE_INVALIDATION_PASS', default='')
