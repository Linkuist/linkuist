"""
    Management command to collect data from reddit
"""

import datetime
import praw
import sys
import urlparse

from redis import Redis
from rq import use_connection, Queue

from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth import models as auth_models
from django.conf import settings

from semantism.process import index_url
from source import models as source_models




class Command(BaseCommand):
    args = ''
    help = u'collect data from reddit'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.reddit = praw.Reddit('Linkuist reddit sumarizer')
        self.reddit.set_oauth_app_info(client_id=settings.REDDIT_APP_ID,
                client_secret=settings.REDDIT_API_SECRET,
                redirect_uri='http://linkuist.com/complete/reddit/')

        self.q = Queue('link_indexing', connection=Redis('127.0.0.1', port=6379))


    def fetch_user_subreddit(self, user):
        auth_extra = user.social_auth.get(provider='reddit')

        # first, set the creds
        self.reddit.set_access_credentials(scope=set(['identity', 'mysubreddits']),
                access_token=auth_extra.extra_data['access_token'],
                refresh_token=auth_extra.extra_data['refresh_token'])

        # refresh our auth tokens
        refreshed_auth = self.reddit.refresh_access_information()
        auth_extra.extra_data['access_token'] = refreshed_auth['access_token']
        auth_extra.extra_data['refresh_token'] = refreshed_auth['refresh_token']
        auth_extra.save()

        for subreddit in self.reddit.get_my_subreddits():
            last = None
            instance, created = source_models.Reddit.objects.get_or_create(subreddit=subreddit.display_name)
            instance.users.add(user)
            for post in subreddit.get_new():
                if post.is_self:
                    continue
                if last is None:
                    last = post.id
                if instance.uid and instance.uid > post.id:
                    print("last stored: %s post: %s" % (instance.uid, post.id))
                    continue

                created_at = datetime.datetime.fromtimestamp(post.created)
                urlp = urlparse.urlparse(post.url)
                self.q.enqueue_call(func=index_url, args=(post.url, [user.id],
                    created_at, 'r/%s' % subreddit.display_name, "Reddit"), timeout=60)
                print("%s enqueued" % post.url)
            instance.uid = last
            instance.save()



    def fetch_mapping(self, user_qs):
        """Build a dict of subreddit and list of users"""
        mapping = {}
        for user in user_qs:
            self.fetch_user_subreddit(user)

    def handle(self, *args, **kwargs):
        users = auth_models.User.objects.filter(social_auth__provider='reddit')

        user_subreddit_mapping = self.fetch_mapping(users)
