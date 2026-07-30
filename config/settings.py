import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-un2mcq!6ux6-o@v#90^fj##=f1(ekw2(&7_!3@@wqicr0xtzfi'

# Security & Debug
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-un2mcq!6ux6-o@v#90^fj##=f1(ekw2(&7_!3@@wqicr0xtzfi')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom apps
    'apps.authentication',
    'apps.classification',
    'apps.dashboard',
    'apps.influencers',
    'apps.uploads',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'],
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


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'influencer_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# Custom User Model Configuration
# ==========================================
AUTH_USER_MODEL = 'authentication.User'

# ==========================================
# Authentication & Session Configuration
# ==========================================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'login'

# Session Security
SESSION_COOKIE_AGE = 1209600  # 2 weeks (in seconds)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Overridden by 'Remember Me' logic in views
SESSION_COOKIE_HTTPONLY = True  # Prevents XSS access to session cookie
SESSION_COOKIE_SECURE = False   # Set to True in production with HTTPS

# ==========================================
# Email Configuration (Development)
# ==========================================
# Prints emails to the console instead of sending them.
# For production, configure SMTP settings using environment variables.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ==========================================
# OpenRouter AI Configuration
# ==========================================
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_MODEL_NAME = os.getenv('OPENROUTER_MODEL_NAME', 'nvidia/nemotron-3-ultra-550b-a55b:free')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_TIMEOUT = int(os.getenv('OPENROUTER_TIMEOUT', 30))
OPENROUTER_MAX_RETRIES = int(os.getenv('OPENROUTER_MAX_RETRIES', 3))