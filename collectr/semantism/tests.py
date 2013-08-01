# -*- coding: utf-8 -*-
"""
    Tests for semantism app
"""

# django
from django.utils import unittest, timezone
from django.test import TransactionTestCase

# project
import oembed
from source import factories as source_factories
from source import models as source_models


from .link import Link, LinkExtractor
from .process import index_url


class LinkTestCase(unittest.TestCase):

    def test_valid_url(self):
        l = Link('')
        self.assertFalse(l.is_valid())

    def test_useless_querystring(self):
        url = """http://www.freenews.fr/spip.php?article12674&utm_source=feedburner&utm_medium=feed&utm_campaign=Feed:+Freenews-Freebox+(Freenews+:+L'actualit%C3%A9+des+Freenautes+-+Toute+l'actualit%C3%A9+pour+votre+Freebox)"""
        l = Link(url)
        self.assertEqual(l.clean(), 'http://www.freenews.fr/spip.php?article12674')

    def test_useless_anchor(self):
        url = """http://www.lemonde.fr/sciences/article/2012/09/10/arianespace-dix-lancements-en-2012-davantage-prevus-l-an-prochain_1758191_1650684.html#xtor=RSS-3208"""
        l = Link(url)
        self.assertEqual(l.clean(), 'http://www.lemonde.fr/sciences/article/2012/09/10/arianespace-dix-lancements-en-2012-davantage-prevus-l-an-prochain_1758191_1650684.html')

    def test_url_encode(self):
        l = Link('')

        ret = l.rebuild_query({'toto': 'tata', 'tutu': ['coin', 'pouet']})
        self.assertEqual(ret, "tutu=coin&tutu=pouet&toto=tata")
        ret = l.rebuild_query({'toto': None, 'tutu': ['coin', 'pouet']})
        self.assertEqual(ret, "tutu=coin&tutu=pouet&toto")

class LinkExtractorTestCase(TransactionTestCase):

    def test_extract_html(self):
        l = LinkExtractor('http://www.lemonde.fr/sciences/article/2012/09/10/arianespace-dix-lancements-en-2012-davantage-prevus-l-an-prochain_1758191_1650684.html')
        l.fetch_url_content()
        self.assertIsNotNone(l.response)

        l.extract()
        self.assertIsNotNone(l.raw_content)
        self.assertIsNotNone(l.full_content)
        self.assertIsNotNone(l.summary)
        self.assertIsNotNone(l.content_type)
        self.assertIsNotNone(l.status_code)
        self.assertIsNotNone(l.title)

    def test_get_summary(self):
        l = LinkExtractor('url')
        text_content = """Le Lorem Ipsum est simplement du faux texte employé dans la composition et la mise en page avant impression. Le Lorem Ipsum est le faux texte standard de l'imprimerie depuis les années 1500, quand un peintre anonyme assembla ensemble des morceaux de texte pour réaliser un livre spécimen de polices de texte. Il n'a pas fait que survivre cinq siècles, mais s'est aussi adapté à la bureautique informatique, sans que son contenu n'en soit modifié. Il a été popularisé dans les années 1960 grâce à la vente de feuilles Letraset contenant des passages du Lorem Ipsum, et, plus récemment, par son inclusion dans des applications de mise en page de texte, comme Aldus PageMaker."""
        summary = l.get_summary(text_content, max_length=300)
        self.assertEqual(summary, "Le Lorem Ipsum est simplement du faux texte employé dans la composition et la mise en page avant impression.")

    def test_url_cleaned(self):
        url = """http://www.freenews.fr/spip.php?article12674&utm_source=feedburner&utm_medium=feed&utm_campaign=Feed:+Freenews-Freebox+(Freenews+:+L'actualit%C3%A9+des+Freenautes+-+Toute+l'actualit%C3%A9+pour+votre+Freebox)"""
        l = LinkExtractor(url)
        self.assertEqual(l.url, 'http://www.freenews.fr/spip.php?article12674')
        l.fetch_url_content()
        l.extract()
        self.assertEqual(l.url, 'http://www.freenews.fr/spip.php?article12674')


class IndexUrlTestCase(TransactionTestCase):

    def setUp(self):
        self.url = "http://www.lemonde.fr/sciences/article/2012/09/10/arianespace-dix-lancements-en-2012-davantage-prevus-l-an-prochain_1758191_1650684.html"
        self.source = source_factories.SourceFactory()
        self.author = source_factories.AuthorFactory()
        self.user = source_factories.UserFactory()

    def test_link_index(self):
        index_url(self.url, self.user.id, timezone.now(), self.author.name, self.source.name)
        index_url(self.url, self.user.id, timezone.now(), self.author.name, self.source.name)

        self.assertEqual(source_models.Url.objects.filter(link=self.url).count(), 1)
        self.assertEqual(source_models.LinkSum.objects.filter(user=self.user).count(), 1)

    def test_link_from_two(self):
        another_user = source_factories.UserFactory()
        index_url(self.url, self.user.id, timezone.now(), self.author.name, self.source.name)
        index_url(self.url, another_user.id, timezone.now(), self.author.name, self.source.name)

        self.assertEqual(source_models.Url.objects.filter(link=self.url).count(), 1)
        self.assertEqual(source_models.LinkSum.objects.filter(url__link=self.url).count(), 2)

    def test_move_to_collection(self):
        url = 'http://www.freenews.fr/spip.php?article12674'
        mfilter = source_factories.FilterFactory(regexp='.*freenews\.fr.*', field='link')
        lsum_id = index_url(url, self.user.id, timezone.now(), self.author.name, self.source.name)
        lsum = source_models.LinkSum.objects.get(pk=lsum_id).select_related('collection')
        self.assertEqual(mfilter.to_collection, lsum.collection)


class OembedTestCase(unittest.TestCase):
    
    def generic_resolve(self, url):
        return oembed.resolve(url)

    def test_flickr_oembed(self):
        res = self.generic_resolve('http://www.flickr.com/photos/vineolia/7052933661/sizes/c/in/set-72157629134495052/')
        self.assertIsNotNone(res)

    def test_youtube_oembed(self):
        res = self.generic_resolve('https://www.youtube.com/watch?v=w9n7KNnFNU8')
        self.assertIsNotNone(res)

    def test_dailymotion_oembed(self):
        res = self.generic_resolve('http://www.dailymotion.com/video/xve2xv_zapping-tele-du-26-11-2012_tv')
        self.assertIsNotNone(res)

    def test_vimeo_oembed(self):
        res = self.generic_resolve('http://vimeo.com/53578987')
        self.assertIsNotNone(res)

    def test_soundcloud_oembed(self):
        res = self.generic_resolve('http://soundcloud.com/pissedoffgil/speakers-so-lowd')
        self.assertIsNotNone(res)
