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

os.environ['DJANGO_SETTINGS_MODULE'] ='collectr.settings_celery'

from collectr import settings_celery
from django.core.management import setup_environ
setup_environ(settings_celery)

# django
from django.contrib.auth.models import User

# semantism
from semantism.tasks import TwitterStatus
from source.models import Rss

if __name__ == "__main__":
    rss_feeds = Rss.objects.all()

    for rss_feed in rss_feeds:
        feed = feedparser.parse(rss_feed.link)

        urlp = urlparse.urlparse(rss_feed.link)
        if hasattr(rss_feed, "etag") and feed['etag'] != rss_feed.etag:
            print "new entry in feed %s" % rss_feed.link
            for entry in feed.entries:
                date_published = datetime(*entry.published_parsed[:-3])

                for user in rss_feed.users.all():
                    TwitterStatus.apply_async(args=(entry['link'], user.pk,
                                              date_published, urlp.netloc,
                                              "Rss"))
            rss_feed.etag = feed['etag']
            rss_feed.save()
            time.sleep(1)
        else:
            print "feed %s not updated" % rss_feed.link

