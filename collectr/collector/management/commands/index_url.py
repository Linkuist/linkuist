"""
    Simple command to run a test from cmdline
"""
# python
import datetime

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


    def handle(self, *args, **kwargs):
        url, user_id, author_name, source = args
        self.q = Queue('tweet_collector', connection=Redis('127.0.0.1', port=6379))
        self.q.enqueue(index_url, url, user_id, datetime.datetime.now(), author_name, source)

