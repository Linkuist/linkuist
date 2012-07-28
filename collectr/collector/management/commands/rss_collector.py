"""
    Management command to start the rss fetcher
"""

import sys
import datetime

from redis import Redis
from rq import use_connection
from rq_scheduler import Scheduler

from django.core.management.base import BaseCommand, CommandError

from collector.rss import fetch_rss

class Command(BaseCommand):
    args = ''
    help = 'start a scheduled rss collection'


    def handle(self, *args, **kwargs):
        scheduler = Scheduler('rss_collector', connection=Redis('127.0.0.1', port=6379))
        scheduler.enqueue(
            datetime.datetime.now(),
            func=fetch_rss,
            interval=360,
        )

