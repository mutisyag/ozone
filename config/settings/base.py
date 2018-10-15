"""
Base settings to build other settings files upon.
"""

import os
import datetime
import environ
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured


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
TIME_ZONE = 'UTC'
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
        'NAME': env.get_value('POSTGRES_DB'),
        'HOST': env.get_value('POSTGRES_HOST'),
        'USER': env.get_value('POSTGRES_USER'),
        'PASSWORD': env.get_value('POSTGRES_PASSWORD'),
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
    'django.contrib.admin',
]
THIRD_PARTY_APPS = [
    'crispy_forms',
    'allauth',
    'allauth.account',
    'rest_framework',
    'rest_framework.authtoken',
    'bootstrap_admin',
    'webpack_loader',
    'import_export',
    'guardian',
]
LOCAL_APPS = [
    # Your stuff: custom apps go here
    'ozone.core.apps.CoreConfig',
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
    'allauth.account.auth_backends.AuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
]

TOKEN_EXPIRE_INTERVAL = datetime.timedelta(days=get_int_env_var('TOKEN_EXPIRE_INTERVAL'))


# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = 'core.User'
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = 'account_login'

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
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = ROOT_DIR / 'static'
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / 'media')
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'





# TODO: this part should be synchronized with Webpack
# (see /frontend/config/conf.js)
_WEBPACK_DIST_DIR = ROOT_DIR / 'frontend' / 'dist'

# TODO: enable this only in production. (this is just a hack
# because the staticfiles app breaks if the directory doesn't exist.)

if _WEBPACK_DIST_DIR.is_dir():
    STATICFILES_DIRS = (
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
            ROOT_DIR / 'templates',
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


# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
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


# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = 'username'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ADAPTER = 'ozone.users.adapters.AccountAdapter'


# Your stuff...
# ------------------------------------------------------------------------------
