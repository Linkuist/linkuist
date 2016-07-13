#!/usr/bin/env python
"""
    Fetch tweets, and store them in the messager broker


"""

import json
import logging
import time
from datetime import datetime
from multiprocessing import Pool

# 3rdparty
import tweepy
from redis import Redis
from rq import Queue

# django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from social.apps.django_app.default.models import UserSocialAuth

# project
from semantism.process import index_url

logger = logging.getLogger('tweet_collector')

CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET


class Command(BaseCommand):
    args = '<username> <username>'
    help = u'collect urls from twitter'

    def handle(self, *args, **kwargs):
        user_list = args
        if not user_list:
            user_list = UserSocialAuth.objects \
                .filter(provider='twitter') \
                .values_list('user__username', flat=True)
        logger.info("Running Twitter URL collector for %s",
                    ", ".join(user_list))

        pool = Pool()
        pool.map(run_process, user_list)
        pool.close()
        pool.join()


class TwitterListener(tweepy.streaming.StreamListener):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(TwitterListener, self).__init__(*args, **kwargs)
        self.queue = Queue('link_indexing',
                           connection=Redis(**settings.RQ_DATABASE))

    def on_error(self, status_code):
        logger.error("Twitter error with status code %s", status_code)

    def on_status(self, status):
        if hasattr(status, 'entities') and 'urls' in status.entities:
            logger.info("Indexing tweet %s for %s",
                        str(status), self.user.username)
            self.queue.enqueue_call(
                func=index_url,
                args=(status, self.user.pk, datetime.now(),
                      status.user.screen_name, "twitter"),
                timeout=60
            )
        else:
            logger.info("tweet ignored")


def run_process(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        logger.error("User %s does not exist", username)
        return -1

    auth_dict = UserSocialAuth.objects.values().get(user__id=user.pk, provider='twitter')['extra_data']
    d = json.loads(auth_dict)
    access_key = d['access_token']
    d = dict([x.split("=") for x in access_key.split("&")])
    ACCESS_KEY = d['oauth_token']
    ACCESS_SECRET = d['oauth_token_secret']
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

    listener = TwitterListener(api=tweepy.API(auth_handler=auth), user=user)
    stream = tweepy.streaming.Stream(auth, listener, secure=True)
    while True:
        try:
            stream.userstream()
        except KeyboardInterrupt:
            break
        except Exception:
            logger.exception('Error while following tweets for %s', username)
            time.sleep(20)
