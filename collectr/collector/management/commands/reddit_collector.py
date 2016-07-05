"""
    Management command to collect data from reddit
"""

import datetime
import logging
import sys
import urlparse

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse

import praw
from redis import Redis
from rq import Queue, use_connection
from social.apps.django_app.utils import load_strategy

from collectr.semantism.process import index_url
from collectr.source import models as source_models

logger = logging.getLogger('collector.reddit')


class Command(BaseCommand):
    args = ''
    help = u'collect data from reddit'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.reddit = praw.Reddit(
                'Linkuist reddit sumarizer',
                disable_update_check=True
        )
        self.reddit.set_oauth_app_info(
            settings.SOCIAL_AUTH_REDDIT_KEY,
            settings.SOCIAL_AUTH_REDDIT_SECRET,
            reverse('social:complete', args=('reddit',))
        )

        self.q = Queue('link_indexing', connection=Redis(**settings.RQ_DATABASE))


    def fetch_user_subreddit(self, user):
        strategy = load_strategy()
        auth_social = user.social_auth.get(provider='reddit')

        logger.debug('Refreshing token for %s', user.username)
        auth_social.refresh_token(
            strategy=strategy,
            redirect_uri=reverse('social:complete', args=('reddit',))
        )
        import json
        auth_social.extra_data = json.loads(auth_social.extra_data)

        logger.debug('Setting credentials for %s', user.username)
        self.reddit.set_access_credentials(
            set(['identity', 'mysubreddits']),
            auth_social.access_token,
        )

        logger.info('Fetching subreddit for user %s', user.username)
        for subreddit in self.reddit.get_my_subreddits():
            print('Working on', subreddit)
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
        self.stdout.write('Processing %d users' % len(users))

        user_subreddit_mapping = self.fetch_mapping(users)
