#!/usr/bin/env python
"""
    Fetch tweets, and store them in the messager broker


"""

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
from django.contrib.auth.models import User
from social_auth.models import UserSocialAuth

# semantism
from semantism.tasks import TwitterStatus


CONSUMER_KEY = 'EsceUi91emhQAtiWQBg'
CONSUMER_SECRET = 'wfFB4l79lfBGJ8dilex6x4Bf2I2imwDXPiNnFcIBdRE'


class TwitterListener(tweepy.streaming.StreamListener):

    def on_status(self, status):
        if hasattr(status, 'entities') and 'urls' in status.entities:
            print "adding task called", datetime.now()
            TwitterStatus.apply_async(args=(status, self.user.pk, datetime.now(), status.user.screen_name, "twitter"))
        else:
            print "ignored"

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
        print "User %s does not exist" % self.user
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
            print exc
            time.sleep(20)

