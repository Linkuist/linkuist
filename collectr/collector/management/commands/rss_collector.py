# -*- coding: utf-8 -*-

"""
    Management command to start the rss fetcher
"""

# python
import datetime

# 3rd party
import redis
from rq import Connection
from rq_scheduler import Scheduler

# django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# collectr
from collector.rss import fetch_rss


class Command(BaseCommand):
    args = ''
    help = 'Starts a scheduled rss collection'

    def handle(self, *args, **kwargs):

        with Connection(redis.Redis(**settings.RQ_DATABASE)):
            scheduler = Scheduler('rss_collector')

            jobs = scheduler.get_jobs()
            for job in jobs:
                if job.func_name == 'collector.rss.fetch_rss':
                    raise CommandError('RSS collector task already scheduled')

            try:
                scheduler.enqueue_periodic(
                    datetime.datetime.now(),
                    1200,
                    20000,
                    fetch_rss,
                )
            except redis.exceptions.ConnectionError:
                raise CommandError('Redis did not respond')
