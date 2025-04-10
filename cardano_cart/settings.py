"""
Django settings for cardano_cart project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from datetime import timedelta
import os
from dotenv import load_dotenv
from pathlib import Path
import dj_database_url
import logging
from django.core.management.utils import get_random_secret_key


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Now use the environment variables in settings
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY', get_random_secret_key())


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

logger = logging.getLogger(__name__)

#ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(" ")
ALLOWED_HOSTS = ['http://localhost:3000', '*']
logger.warning(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")

ALLOWED_HOSTS = [
    "charming-ninnetta-knust-028ea081.koyeb.app",
    "localhost",
    "127.0.0.1",
]




# Application definition

INSTALLED_APPS = [
    'corsheaders',  # Add this
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_spectacular',
    'rest_framework_swagger',
    'users',
    'products',
    'orders',
    'payments',
    'reviews',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this at the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://charming-ninnetta-knust-028ea081.koyeb.app",
    'http://localhost:3000',
]

CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "False").lower() == "true"

ROOT_URLCONF = 'cardano_cart.urls'


CSRF_ALLOWED_METHODS = [
    'POST',
    'GET',
    'DELETE',
    'PUT',
    'OPTIONS',
]

CSRF_TRUSTED_ORIGINS = [
    "https://charming-ninnetta-knust-028ea081.koyeb.app"
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
}

SPECTACULAR_SETTINGS = {
    "TITLE": 'Cardano Cart API',
    "DESCRIPTION": 'API for Cardano Cart',
    "VERSION": '1.0.0',
    "CONTACT": 'Jimmy Essel',
    "TERMS_OF_SERVICE": None,
    "LICENSE": None,

}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(weeks=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # Use your secret key
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cardano_cart.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'require'}
}
}


#DATABASES["default"] = dj_database_url.parse("postgresql://cardano_cart_database_user:FmZnCacyg8QMUqjU7iVF7MWMlvBGYAsV@dpg-crmq5ba3esus7381ov3g-a.oregon-postgres.render.com/cardano_cart_database")

# 


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'

AUTHENTICATION_BACKENDS = [
    'users.backends.EmailBackend',  # Add this line
    'django.contrib.auth.backends.ModelBackend',  # Keep the default backend if needed
]


SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}