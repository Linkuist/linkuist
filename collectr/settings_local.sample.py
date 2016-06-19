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

RQ_DATABASE = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
}

SECRET_KEY = ''

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
