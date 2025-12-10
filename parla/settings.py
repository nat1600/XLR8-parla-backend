"""
Django settings for parla project.
"""
import dj_database_url
from pathlib import Path
import os


def require_env(name: str) -> str:
    """Return required environment variable or raise a clear error."""
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"{name} environment variable is required")
    return value


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return str(value).lower() in {"1", "true", "t", "yes", "y", "on"}
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = require_env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool('DEBUG', default=False)

# FRONTEND_URL desde .env
FRONTEND_URL = os.getenv('FRONTEND_URL', '').strip()

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
]
if FRONTEND_URL:
    ALLOWED_HOSTS.append(FRONTEND_URL)


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    # Third party
    'rest_framework',
    'corsheaders',
    
    # APPS FROM OUR PROJECT 
    'users',
    'phrases', 
    'flashcards',
    'gamification',
]

# ← IMPORTANt: userrr
AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'users.middleware.CSRFExemptAPIMiddleware',  # ← Eximir CSRF para /api/
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'users.middleware.JWTAuthenticationMiddleware',  # ← JWT desde cookie
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'parla.urls'

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

WSGI_APPLICATION = 'parla.wsgi.application'


# Database - NEON
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=require_env('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-alidators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-co'  # ← Cambiado a español Colombia
TIME_ZONE = 'America/Bogota'  # ← Zona horaria Bogotá

USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS Settings 

CORS_ALLOW_ALL_ORIGINS = False  # Cambiar a False por seguridad
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "chrome-extension://moehmphhjgmgonplmjeaglfkolcklpkh",
]
if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)
CORS_ALLOW_CREDENTIALS = True  # ← IMPORTANTE para cookies
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "chrome-extension://moehmphhjgmgonplmjeaglfkolcklpkh",
]
if FRONTEND_URL:
    CSRF_TRUSTED_ORIGINS.append(FRONTEND_URL)


# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ]
}

# DeepL API Key
DEEPL_API_KEY = require_env('DEEPL_API_KEY')

# Google OAuth settings
GOOGLE_CLIENT_ID = require_env('GOOGLE_CLIENT_ID')
