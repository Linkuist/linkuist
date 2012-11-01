"""
    Test for our link_tracking app
"""

from django.core.urlresolvers import reverse
from django.test import TransactionTestCase

from source import factories as source_factories


class LinkTrackingTestCase(TransactionTestCase):

    def setUp(self):
        self.user = source_factories.UserFactory()
        self.user.set_password('toto')
        self.user.save()
        self.client.login(username=self.user.username, password='toto')

    def test_track_link(self):
        url = source_factories.UrlFactory(link="http://google.com")
        linksum = source_factories.LinkSumFactory(url=url, user=self.user)
        response = self.client.get(
            reverse('link_tracking:track_link', kwargs={'link_id': linksum.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', url.link))
