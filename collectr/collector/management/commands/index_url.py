"""
    Simple command to run a test from cmdline
"""
# python
import datetime
from optparse import make_option

# django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

# collectr
from semantism.process import index_url

# rq
import redis
from rq import Queue, Connection


class Command(BaseCommand):
    args = '<url> <user> <author name> <source>'
    help = 'insert an url in link_indexing queue'
    option_list = BaseCommand.option_list + (
        make_option('--sync',
            action='store_true',
            dest='sync',
            default=False,
            help="don't send the request to rq if True"),
        )

    def handle(self, *args, **kwargs):
        url, username, author_name, source = args
        print kwargs

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User {0} does not exist.'.format(username))

        if 'sync' in kwargs:
            index_url(url, user.id, datetime.datetime.now(), author_name,
                      source)
        else:
            with Connection(redis.Redis(**settings.RQ_DATABASE)):
                queue = Queue('link_indexing')
                queue.enqueue(index_url, url, user.id,
                              datetime.datetime.now(), author_name, source)

