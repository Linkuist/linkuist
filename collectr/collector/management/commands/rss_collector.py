"""
    Management command to start the rss fetcher
"""

import sys
import datetime

import redis
from rq import Connection
from rq_scheduler import Scheduler

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from collector.rss import fetch_rss

class Command(BaseCommand):
    args = ''
    help = 'start a scheduled rss collection'


    def handle(self, *args, **kwargs):

        with Connection(redis.Redis(**settings.RQ_DATABASE)):
            scheduler = Scheduler('rss_collector')

            try:
                scheduler.enqueue_periodic(
                    datetime.datetime.now(),
                    1200,
                    20000,
                    fetch_rss,
                )
            except redis.exceptions.ConnectionError:
                raise CommandError('Redis did not respond')
