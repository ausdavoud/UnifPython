import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == "development":
    DEBUG = True
elif ENVIRONMENT == "production":
    DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    os.environ.get("PRODUCTION_HOSTNAME"),
]


# Application definition

DEFAULT_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = ["django_celery_beat"]

DJANGO_APPS = [
    "common",
    "lms_public",
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + DJANGO_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core_config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core_config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# settings.py
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")  # Use Redis as broker
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": 3600,  # 1 hour
}
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

if ENVIRONMENT == "production":
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ORIGIN_WHITELIST = []
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True

    CSRF_TRUSTED_ORIGINS = [f"http://{os.environ.get("PRODUCTION_HOSTNAME")}"]
    ssl_env = os.environ.get("USE_SSL", 'False')
    if ssl_env.lower() == "true":
        CSRF_TRUSTED_ORIGINS = [f"https://{os.environ.get("PRODUCTION_HOSTNAME")}"]
        CSRF_COOKIE_SECURE = True
        SESSION_COOKIE_SECURE = True
        SECURE_SSL_REDIRECT = True

    SECURE_HSTS_SECONDS = 31536000 # one year
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
