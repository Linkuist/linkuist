# -*- coding: utf-8 -*-
from settings import *

DEBUG = False

#BROKER_HOST = "localhost"
#BROKER_PORT = 5672
#BROKER_USER = "guest"
#BROKER_PASSWORD = "guest"
#BROKER_VHOST = "/"
#CELERY_RESULT_BACKEND = "redis"
#CELERY_REDIS_HOST = "localhost"
#CELERY_REDIS_PORT = 6379
#CELERY_REDIS_DB = 0
BROKER_URL = "redis://localhost:6379/0"

INSTALLED_APPS += (
    'djcelery',
)

import djcelery
djcelery.setup_loader()
