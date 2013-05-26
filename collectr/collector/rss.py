#!/usr/bin/env python
"""
    Fetch rss and store them in the message broker

"""

import feedparser
import os
import sys
import time
import urlparse

from datetime import datetime

sys.path.append('../')
sys.path.append('../../')

os.environ['DJANGO_SETTINGS_MODULE'] ='collectr.settings'

from collectr import settings
from django.core.management import setup_environ
setup_environ(settings)

# django
from django.contrib.auth.models import User

# semantism
from source.models import Rss
from semantism.process import index_url

# rq
import redis
from rq import Queue, Connection


def fetch_rss():
    rss_feeds = Rss.objects.all()
    with Connection(redis.Redis(**settings.RQ_DATABASE)):
        q = Queue('link_indexing')

        for rss_feed in rss_feeds:
            feed = feedparser.parse(rss_feed.link)

            urlp = urlparse.urlparse(rss_feed.link)
            if 'etag' in feed and feed['etag'] != rss_feed.etag:
                print "new entry in feed %s" % rss_feed.link
                for entry in feed.entries:
                    date_pub = entry.get('published_parsed') or entry.get('updated_parsed')
                    if not date_pub:
                        print "can't find date_pub"
                        continue
                    date_published = datetime(*date_pub[:-3])

                    user_id_list = list(rss_feed.users.values_list('id', flat=True))
                    time.sleep(1)

                    q.enqueue_call(func=index_url, args=(entry['link'], user_id_list,
                            date_published, urlp.netloc, "Rss"), timeout=60)
                rss_feed.etag = feed['etag']
                rss_feed.save()
            else:
                print "feed %s not updated" % rss_feed.link_at

if __name__ == '__main__':
    fetch_rss()
