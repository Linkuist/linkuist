# -*- coding: utf-8 -*-

"""
    unstack links and index them'

"""

# python
import logging

# django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# rq
import redis
from rq import Queue, Connection, Worker

# raven (sentry)
try:
    from raven import Client
    from rq.contrib.sentry import register_sentry
    HAS_SENTRY = True
except ImportError:
    HAS_SENTRY = False

# import django's models to preload code
from source import models as source_models


class Command(BaseCommand):
    args = u'<queue_name>'
    help = u'Run worker for the queue'

    def handle(self, *args, **options):

        logger = logging.getLogger(__name__)
        queue_name = args[0] if args else 'link_indexing'

        with Connection(redis.Redis(**settings.RQ_DATABASE)):
            queue = Queue(queue_name)
            peon = Worker(queue)

            if HAS_SENTRY:
                sclient = Client(settings.SENTRY_DSN)
                register_sentry(sclient, peon)

            try:
                peon.work()
            except redis.exceptions.ConnectionError:
                raise CommandError('Redis did not respond')
