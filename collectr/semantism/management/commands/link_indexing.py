"""
    unstack links and index them'

"""


# django
from django.conf import settings
from django.core.management.base import BaseCommand

# rq
from rq import Queue, Connection, Worker

# raven (sentry)
from raven import Client
from rq.contrib.sentry import register_sentry

# import django's models to preload code
from source import models as source_models


class Command(BaseCommand):
    args = u"<queue_name>"
    help = u"Run worker for the queue"

    def handle(self, *args, **options):
        queue_name = 'link_indexing'
        if args:
            queue_name = args[0]
        with Connection():
            qs = Queue(queue_name)
            w = Worker(qs)
            sclient = Client(settings.SENTRY_DSN)
            register_sentry(sclient, w)
            w.work()



