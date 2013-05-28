from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


from source import factories as source_factories


class RssTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = source_factories.UserFactory()
        self.user.set_password('toto')
        self.user.save()

    def test_add_rss(self):
        url = reverse('userprofile:add_rss')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        result = self.client.login(username=self.user.username, password='toto')
        self.assertTrue(result)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)

        data = {
            'link': 'http://www.myfeeds.com/feed',
            'name': 'myfeed'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('userprofile:rss'))
