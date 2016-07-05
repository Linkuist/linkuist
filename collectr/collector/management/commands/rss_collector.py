# -*- coding: utf-8 -*-

"""
    Management command to start the rss fetcher
"""

# python
import datetime
from optparse import make_option

# 3rd party
import redis
from rq import Connection
from rq_scheduler import Scheduler

# django
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# collectr
from collectr.collector.rss import fetch_rss


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--replace',
            action='store_true',
            dest='replace',
            default=False,
            help='Replace an existing RSS collecting job.'),
        )
    help = 'Starts a scheduled rss collection'

    def handle(self, *args, **options):

        with Connection(redis.Redis(**settings.RQ_DATABASE)):
            scheduler = Scheduler('rss_collector')

            jobs = scheduler.get_jobs()
            for job in jobs:
                if job.func_name != 'collector.rss.fetch_rss':
                    continue

                if options.get('replace'):
                    job.cancel()
                    break
                else:
                    raise CommandError('RSS collector task already scheduled')

            try:
                scheduler.schedule(
                    datetime.datetime.now(),
                    fetch_rss,
                    interval=1200,
                    repeat=20000,
                )
            except redis.exceptions.ConnectionError:
                raise CommandError('Redis did not respond')
