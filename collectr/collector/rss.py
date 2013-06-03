#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Fetch rss and store them in the message broker
"""

# python
import logging
import os
import sys
import time
import urlparse
from datetime import datetime

# 3rd party
import feedparser
import redis
from rq import Queue, Connection

sys.path.append('../')
sys.path.append('../../')

os.environ['DJANGO_SETTINGS_MODULE'] = 'collectr.settings'


from django.conf import settings

# semantism
from source.models import Rss
from semantism.process import index_url


def fetch_rss():
    logger = logging.getLogger(__name__)
    rss_feeds = Rss.objects.all()

    with Connection(redis.Redis(**settings.RQ_DATABASE)):
        queue = Queue('link_indexing')

        for rss_feed in rss_feeds:
            feed = feedparser.parse(rss_feed.link, etag=rss_feed.etag)
            if feed.status > 399:
                logger.warning('Got bad http status while fetching %s', rss_feed.link)
                continue

            if feed.status == 304:
                logger.info('Feed %s not modified', rss_feed.link)
                continue

            if feed.bozo:
                logger.warning('Problem while parsing feed %s (%s)', 
                    rss_feed.link, feed.bozo_exception)
                continue
            urlp = urlparse.urlparse(feed['feed']['link'])

            if feed.get('etag') != rss_feed.etag:
                logger.info('New entry in feed %s', rss_feed.link)
                rss_feed.etag = feed['etag']
                rss_feed.save()

            else:
                logger.info('Feed %s does not support etag', rss_feed.link)

            for entry in feed.entries:
                date_pub = entry.get('published_parsed') or \
                    entry.get('updated_parsed')
                if not date_pub:
                    logger.warning('Cannot find date_pub in feed %s',
                                   rss_feed.link)
                    continue
                date_published = datetime(*date_pub[:-3])

                user_id_list = list(rss_feed.users.values_list('id',
                                                               flat=True))
                time.sleep(1)

                queue.enqueue_call(func=index_url, args=(
                    entry['link'], user_id_list, date_published,
                    urlp.netloc, "Rss"
                ), timeout=60)

            else:
                logger.info('Feed %s not updated', rss_feed.link)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    fetch_rss()
