#!/usr/bin/env python
"""
    Fetch rss and store them in the message broker

"""

import feedparser
import os
import pprint
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
from semantism import index_url

# rq
from redis import Redis
from rq import use_connection, Queue


def fetch_rss():
    rss_feeds = Rss.objects.all()
    q = Queue('link_indexing', connection=Redis('127.0.0.1', port=6379))

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


                for user in rss_feed.users.all():
                    q.enqueue(index_url, entry['link'], user.pk, date_published, urlp.netloc, "Rss")
            rss_feed.etag = feed['etag']
            rss_feed.save()
            time.sleep(1)
        else:
            print "feed %s not updated" % rss_feed.link

if __name__ == '__main__':
    fetch_rss()
