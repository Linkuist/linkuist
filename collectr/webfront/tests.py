"""
    Test for our webfront app
"""

from django.core.urlresolvers import reverse
from django.test import TransactionTestCase

from source import factories as source_factories


class WebfrontTestCase(TransactionTestCase):

    def setUp(self):
        user = source_factories.UserFactory()
        user.set_password('toto')
        user.save()
        self.client.login(username=user.username, password='toto')

    def test_collection(self):
        response = self.client.get(reverse('webfront:collection'))
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        response = self.client.get(
            reverse('webfront:search'), {'query': 'search_token'})
        self.assertEqual(response.status_code, 200)

    def test_redirect(self):
        response = self.client.get(reverse('webfront:collection'))
        self.assertEqual(response.status_code, 200)
