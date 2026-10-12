"""
Django base settings for maktab19 project.
"""
from pathlib import Path
import os
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add apps directory to sys.path so apps can be imported cleanly
sys.path.insert(0, str(BASE_DIR / 'apps'))

# Try to load environment variables using django-environ or python-dotenv or fallback
try:
    import environ
    env = environ.Env(
        DEBUG=(bool, True),
        SECRET_KEY=(str, 'django-insecure-maktab19-school-platform-secret-key-2026'),
        ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost', '*']),
        DATABASE_URL=(str, f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
    )
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
except ImportError:
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE_DIR, '.env'))
    except ImportError:
        pass

    class FallbackEnv:
        def __call__(self, key, default=None, cast=None):
            val = os.getenv(key, default)
            if cast is bool and isinstance(val, str):
                return val.lower() in ('1', 'true', 'yes', 'on')
            if cast is list and isinstance(val, str):
                return [v.strip() for v in val.split(',') if v.strip()]
            if cast and val is not None:
                return cast(val)
            return val

        def bool(self, key, default=False):
            return self(key, default=default, cast=bool)

        def list(self, key, default=None):
            return self(key, default=default or [], cast=list)

        def str(self, key, default=''):
            return str(self(key, default=default))

        def db(self, key='DATABASE_URL', default=None):
            db_url = os.getenv(key, default or f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
            if db_url.startswith('sqlite:///'):
                path = db_url.replace('sqlite:///', '')
                return {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / path if not os.path.isabs(path) else Path(path),
                }
            elif db_url.startswith('postgres://') or db_url.startswith('postgresql://'):
                # Basic postgres url parser
                import urllib.parse
                url = urllib.parse.urlparse(db_url)
                return {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': url.path[1:],
                    'USER': url.username,
                    'PASSWORD': url.password,
                    'HOST': url.hostname,
                    'PORT': url.port or 5432,
                }
            return {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }

    env = FallbackEnv()

SECRET_KEY = env.str('SECRET_KEY', 'django-insecure-maktab19-school-platform-secret-key-2026')
DEBUG = env.bool('DEBUG', True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', ['127.0.0.1', 'localhost', '*'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'apps.core.apps.CoreConfig',
    'apps.news.apps.NewsConfig',
    'apps.teachers.apps.TeachersConfig',
    'apps.contacts.apps.ContactsConfig',
    'apps.achievements.apps.AchievementsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'apps.core.middleware.SessionLanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add whitenoise if available
try:
    import whitenoise
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    pass

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'apps.core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
try:
    if hasattr(env, 'db'):
        DATABASES = {
            'default': env.db('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
except Exception:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('uz', "O'zbek"),
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security & Uploads
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

# Session cookie settings
SESSION_COOKIE_AGE = 86400 * 7  # 7 days
SESSION_SAVE_EVERY_REQUEST = True
