# -*- coding: utf-8 -*-
"""
Collectr's project settings.
"""
import os


PROJECT_PATH = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': '',
#        'USER': '',
#        'PASSWORD': '',
#        'HOST': '',
#        'PORT': '',
#    }
#}

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = ''

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'collectr.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, "templates")
)

INSTALLED_APPS = (
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    
    # External Django apps
    'django_extensions',
    'south',
    'social_auth',
    
    # Project apps
    'collector',
    'source',
    'userprofile',
    'link_tracking',
    'semantism',
    'webfront',
    'tastypie',
)


AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
   "django.contrib.auth.context_processors.auth",
   "django.core.context_processors.request",
   "django.core.context_processors.debug",
   "django.core.context_processors.i18n",
   "django.core.context_processors.media",
   "django.core.context_processors.static",
   "django.contrib.messages.context_processors.messages",
   'social_auth.context_processors.social_auth_by_name_backends',
   'social_auth.context_processors.social_auth_backends',
   'social_auth.context_processors.social_auth_by_type_backends',
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/app/#/links'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    }, 
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'index_url': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
}


TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''

SOUTH_TESTS_MIGRATE = False

try:
    from settings_local import *
except ImportError:
    pass
