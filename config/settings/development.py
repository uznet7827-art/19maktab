"""Development settings for maktab19 project."""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Simple cache for dev
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email backend for development - console output
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
