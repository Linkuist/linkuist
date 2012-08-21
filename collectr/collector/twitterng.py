#!/usr/bin/env python
"""
    Fetch tweets, and store them in the messager broker


"""

import logging
import os
import pprint
import sys
import time

from datetime import datetime

sys.path.append('../')
sys.path.append('../../')

os.environ['DJANGO_SETTINGS_MODULE'] ='collectr.settings'

import simplejson as json

from collectr import settings
from django.core.management import setup_environ
setup_environ(settings)

# 3rdparty
import tweepy

# django
from django.conf import settings
from django.contrib.auth.models import User
from social_auth.models import UserSocialAuth

# rq
from redis import Redis
from rq import use_connection, Queue

from semantism.process import index_url

logger = logging.getLogger('tweet_collector')


CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET


class TwitterListener(tweepy.streaming.StreamListener):

    def __init__(self, *args, **kwargs):
        super(TwitterListener, self).__init__(*args, **kwargs)
        self.q = Queue('link_indexing', connection=Redis('127.0.0.1', port=6379))

    def on_error(self, status_code):
        logger.error("Twitter error with status code %s", status_code)

    def on_status(self, status):
        if hasattr(status, 'entities') and 'urls' in status.entities:
            logger.info("adding task called %s for %s" % (datetime.now(), sys.argv[1]))
            self.q.enqueue(index_url, status, self.user.pk, datetime.now(),
                    status.user.screen_name, "twitter")
        else:
            logger.info("tweet ignored")

def usage():
    print "<%s> <username>" % sys.argv[0]

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        usage()
        sys.exit()
    user = sys.argv[1]

    try:
        user = User.objects.get(username=user)
    except User.DoesNotExist:
        print "User %s does not exist" % user
        sys.exit()

    auth_dict = UserSocialAuth.objects.values().get(user__id=user.pk)['extra_data']
    d = json.loads(auth_dict)
    access_key = d['access_token']
    d = dict([x.split("=") for x in access_key.split("&")])
    ACCESS_KEY = d['oauth_token']
    ACCESS_SECRET = d['oauth_token_secret']
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

    TwitterListener.user = user
    listener = TwitterListener(api=tweepy.API(auth_handler=auth))
    stream = tweepy.streaming.Stream(auth, listener, secure=True)
    while True:
        try:
            stream.userstream()
        except KeyboardInterrupt:
            break
        except Exception, exc:
            print sys.argv[1], exc
            time.sleep(20)

