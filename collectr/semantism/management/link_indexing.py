"""
    unstack links and index them'

"""

# django
from django.core.management.base import BaseCommand

# rq
from rq import Queue, Connection, Worker


class Command(BaseCommand):
    args = u"<queue_name>"
    help = u"Run worker for the queue"

    def handle(self, *args, **options):
        queue_name = 'link_indexing'
        if args:
            queue_name = args[0]
        with Connection():
            qs = map(Queue, queue_name) or [Queue()]

            w = Worker(qs)
            w.work()
        


