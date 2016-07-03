"""
    Test the collectors (rss, twitter, reddit ...)
"""

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, TransactionTestCase

import redis

from source import models as source_models
from source import factories as source_factories
from userprofile.models import UserProfile

from . import rss as rss_module

import feedparser


class RssCollectorTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(RssCollectorTestCase, self).__init__(*args, **kwargs)
        self.rss = None
        self.redis_client = redis.Redis(**settings.RQ_DATABASE)

    def tearDown(self):
        self.redis_client.flushdb()

    def make_initial_rss(self):
        self.rss = source_factories.RssFactory()

    def test_rss_collector(self):
        atom_feed = source_factories.RssFactory(
            link='https://github.com/dzen/collectr/commits/master.atom',
            etag=None
        )

        rss_feed = source_factories.RssFactory(
            link='http://www.moto-net.com/rss_actu.xml',
        )
        rss_module.fetch_rss()

        # reload the rss
        atom_feed = source_models.Rss.objects.get(pk=atom_feed.pk)

        self.assertIsNotNone(atom_feed.etag)

        expected_jobs_len = (
            len(feedparser.parse(atom_feed.link)['entries']) +
            len(feedparser.parse(rss_feed.link)['entries'])
        )
        job_len = len(self.redis_client.keys('rq:job:*'))
        self.assertEqual(job_len, expected_jobs_len)


class CollectorViewTest(TransactionTestCase):

    def setUp(self):
        self.user = source_factories.UserFactory()
        self.user.set_password('toto')
        self.user.save()
        self.client.login(username=self.user.username, password='toto')

    def test_submit_nolink(self):
        response = self.client.get(reverse('collector:bookmark',
                                           args=(self.user.username,)))
        self.assertEqual(response.status_code, 400)

    def test_submit_invalid_token(self):
        response = self.client.get(
            reverse('collector:bookmark', args=(self.user.username,)) + "?" +
            "&".join(
                key + '=' + value for key, value in {
                    'url': 'http://www.moto-net.com/rss_actu.xml',
                    'from': 'me',
                    'source': 'all',
                    'token': 'pazoeiazeip',
                }.items()
            ))
        self.assertEqual(response.status_code, 403)

    def test_submit_success(self):
        uprofile = UserProfile(user=self.user, token='randomtoken')
        uprofile.save()

        response = self.client.get(
            reverse('collector:bookmark', args=(self.user.username,)) + "?" +
            "&".join(
                key + '=' + value for key, value in {
                    'url': 'http://www.moto-net.com/rss_actu.xml',
                    'from': 'me',
                    'source': 'all',
                    'token': 'randomtoken',
                }.items()
            ))
        self.assertEqual(response.status_code, 202)
