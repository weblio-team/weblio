from pathlib import Path
import os
import dj_database_url
from google.oauth2 import service_account

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-upbpz=nvj$stnporclt2p*#7f2v_#&p=gjmjyu_jnt6cyqwi2t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if 'DYNO' in os.environ else True

ALLOWED_HOSTS = ['.blog', '.herokuapp.com', 'localhost', '127.0.0.1'] if not DEBUG else []

SILENCED_SYSTEM_CHECKS = ['ckeditor.W001', 'templates.W003']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'members',
    'posts',
    'ckeditor',
    'ckeditor_uploader',
    'storages',
    'simple_history',
    'django_social_share',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'weblio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                os.path.join(BASE_DIR, 'services', 'templates'),
                os.path.join(BASE_DIR, 'posts', 'templates'),
                os.path.join(BASE_DIR, 'members', 'templates'),
            ],
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

WSGI_APPLICATION = 'weblio.wsgi.application'


# Database
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres.eghyyeuzfvyadfurnzji:cincoenIS2*@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
    )
} if not DEBUG else {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
   # {
   #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
   # },
   # {
   #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
   # },
   # {
   #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
   # },
   # {
   #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
   # },
]


# Internationalization
LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Asuncion'

USE_I18N = True

USE_TZ = False

# Redirects
LOGIN_REDIRECT_URL = 'posts'
LOGOUT_REDIRECT_URL = '/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media files
if DEBUG:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        "gcpCredentials.json"
    )
    STORAGES = {
        'default': {
            "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
            "OPTIONS": {
                "bucket_name": "bucket-weblio",
                "credentials": GS_CREDENTIALS,
                "location": "media",
                "default_acl": None,
                "querystring_auth": False,
            }
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = "members.Member"

# Ckeditor settings
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', 'Blockquote']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'CodeSnippet']},
            {'name': 'styles', 'items': ['Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize']},
        ],
        'skin': 'moono-lisa',
        'codeSnippet_theme': 'monokai',
        'extraPlugins': ','.join(
            [
                'codesnippet',
                'uploadimage',
                'widget',
                'lineutils',
                'clipboard',
            ]
        ),
    },
}

# Lyket settings
LYKET_API_KEY = "pt_3dfda96e132cbc507a6cad39de1826"

# Commentbox settings
COMMENTBOX_API_KEY = "5656563893141504-proj"

# Stripe settings
STRIPE_SECRET_KEY = 'sk_test_51Q0AFPExUxjRx0RpTB80794w8DxRRlgD8j2pe2wADC1kGHe5k2x104Rsr60G9fQi27kp9yqTt5m9fgTA2f32rKQS00fr1cwO3o'
STRIPE_PUBLISHABLE_KEY = 'pk_test_51Q0AFPExUxjRx0Rpl43gBHsax9yrb6rYn5OHWxjecEBCrARC0MsVxnBQkGMHBSJKrh0mv27oMhhOkiHxepLtCozT00vBxQpXLS'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'weblio.team@gmail.com'
EMAIL_HOST_PASSWORD = 'klbohblyoghjdlyo'