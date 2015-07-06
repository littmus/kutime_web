"""
Django settings for kutime project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.conf import settings
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6c+8xg$bv46#gein%f+y=r5iunot*pi^psk%!clrlex-i&-_xy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
#COMPRESS_ENABLED = not DEBUG
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['127.0.0.1','littm.us']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'kutime',

    'gunicorn',
    'compressor',
    'watson',
)

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
    )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'kutime.urls'

WSGI_APPLICATION = 'kutime.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    '_default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'kutime.db',
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'kutime',
	    'USER': 'kutime',
    	'PASSWORD': 'kutime',
    	'HOST': 'localhost',
    	'PORT': '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
if DEBUG:
    STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
else:
    STATIC_ROOT = '/var/www/kutime/static/'

STATICFILES_DIR = (
    os.path.join(SITE_ROOT, 'static'),

)
if not DEBUG:
    STATICFILES_DIR += (
        '/var/www/kutime/static/',
    )

STATICFILES_FINDERS = settings.STATICFILES_FINDERS + (
    'compressor.finders.CompressorFinder',
)

COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio'),
)

if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/kutime_cache',
            'TIMEOUT': 3600,
            'OPTIONS': {
                'MAX_ENTRIES': 512
            }
        }
    }

