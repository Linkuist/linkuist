"""
    Simple command to run a test from cmdline
"""
# python
import datetime
from optparse import make_option

# django
from django.core.management.base import BaseCommand, CommandError

# collectr
from semantism import index_url

# rq
from redis import Redis
from rq import use_connection, Queue


class Command(BaseCommand):
    args = '<url> <user_id> <author name> <source>'
    help = 'insert an url in tweet_collector queue'
    option_list = BaseCommand.option_list + (
        make_option('--sync',
            action='store_true',
            dest='sync',
            default=False,
            help="don't send the request to rq if True"),
        )

    def handle(self, *args, **kwargs):
        url, user_id, author_name, source = args
        print kwargs
        if 'sync' in kwargs:
            index_url(url, user_id, datetime.datetime.now(), author_name, source)
        else:
            self.q = Queue('tweet_collector', connection=Redis('127.0.0.1', port=6379))
            self.q.enqueue(index_url, url, user_id, datetime.datetime.now(), author_name, source)

