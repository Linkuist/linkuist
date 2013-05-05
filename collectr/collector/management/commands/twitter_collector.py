#!/usr/bin/env python
"""
    Fetch tweets, and store them in the messager broker


"""

import json
import logging
import os
import time

from datetime import datetime
from multiprocessing import Process

# 3rdparty
import tweepy
from redis import Redis
from rq import use_connection, Queue

# django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from social_auth.models import UserSocialAuth

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
            user_list = UserSocialAuth.objects.values_list('user__username',
                    flat=True).filter(provider='twitter')
        logger.info("running for %s" % ", ".join(user_list))

        processes = []
        for user in user_list:
            p = Process(target=run_process, args=(user,))
            p.start()
            processes.append(p)

        for process in processes:
            process.join()



class TwitterListener(tweepy.streaming.StreamListener):

    def __init__(self, *args, **kwargs):
        super(TwitterListener, self).__init__(*args, **kwargs)
        self.q = Queue('link_indexing', connection=Redis('127.0.0.1', port=6379))

    def on_error(self, status_code):
        logger.error("Twitter error with status code %s", status_code)

    def on_status(self, status):
        print("received status")
        if hasattr(status, 'entities') and 'urls' in status.entities:
            logger.info("adding task called %s for %s" % (datetime.now(), self.user.username))
            self.q.enqueue_call(func=index_url, args=(status, self.user.pk, datetime.now(),
                    status.user.screen_name, "twitter"), timeout=60)
        else:
            logger.info("tweet ignored")


def run_process(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print "User %s does not exist" % uername
        return -1

    auth_dict = UserSocialAuth.objects.values().get(user__id=user.pk, provider='twitter')['extra_data']
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
            print username, exc
            time.sleep(20)


