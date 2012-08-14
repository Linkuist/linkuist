# -*- coding: utf-8 -*-
"""
Collectr local settings.
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'collectr',
        'USER': 'collectr',
        'PASSWORD': 'collectr',
        'HOST': 'localhost',
        'PORT': '',
    }
}

SECRET_KEY = ''

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
