"""
    Test for our webfront app
"""

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django import test


from source import factories as source_factories
from webfront import views as webfront_views


class WebfrontTestCase(test.TransactionTestCase):

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

    def test_links_today_today(self):
        response = self.client.get(reverse('webfront:links_today', args=('today',)))
        self.assertEqual(response.status_code, 200)

    def test_links_today_yesterday(self):
        response = self.client.get(reverse('webfront:links_today', args=('yesterday',)))
        self.assertEqual(response.status_code, 200)

    def test_links_today_week(self):
        response = self.client.get(reverse('webfront:links_today', args=('this_week',)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('webfront:links_today', args=('last_week',)))
        self.assertEqual(response.status_code, 200)


    def test_links_today_month(self):
        response = self.client.get(reverse('webfront:links_today', args=('this_month',)))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('webfront:links_today', args=('last_month',)))
        self.assertEqual(response.status_code, 200)



class WebfrontPaginationTestCase(test.TestCase):

    def test_pagination_one(self):
        paginator = Paginator(xrange(500), 10)
        page_range = webfront_views.get_display_paginate_item(paginator, 1)
        self.assertEqual(page_range, [1, 2, 3, 4, '...'])

    def test_paginator_two(self):
        paginator = Paginator(xrange(500), 10)
        page_range = webfront_views.get_display_paginate_item(paginator, 2)
        self.assertEqual(page_range, [1, 2, 3, 4, '...'])

    def test_pagination_middle(self):
        paginator = Paginator(xrange(500), 10)
        page_range = webfront_views.get_display_paginate_item(paginator, 40)
        self.assertEqual(page_range, [1, '...', 38, 39, 40, 41, '...', 50])

    def test_pagination_end(self):
        paginator = Paginator(xrange(500), 10)
        page_range = webfront_views.get_display_paginate_item(paginator, 490)
        self.assertEqual(page_range, [1, '...', 45, 46, 47, 48, 49, 50])
        page_range = webfront_views.get_display_paginate_item(paginator, 500)
        self.assertEqual(page_range, [1, '...', 45, 46, 47, 48, 49, 50])
