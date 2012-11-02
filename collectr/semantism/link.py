# -*- coding: utf-8 -*-
"""
    semantism tasks

"""
# python
import logging
import os

import urlparse


DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_1) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4"

# 3rdparty
import requests
from goose.Goose import Goose

# local
from semantism import exceptions as index_exc

logger = logging.getLogger(__name__)


class Link(object):
    """Cleanup and validate a link"""
    def __init__(self, url):
        self.url = url
        self.ignorable_qs = ('utm_source', 'utm_medium', 'utm_campaign', 'xtor')
        self.ignorable_anchor = ('xtor',)

    def is_valid(self, url=None):
        if not url:
            url = self.url
        if not url:
            return False

    def clean_anchors(self, url=None):
        """Cleanup unused #anchors"""
        if not url:
            url = self.url

        u = urlparse.urlparse(url)
        fragment = u.fragment
        qs = urlparse.parse_qs(u[5], keep_blank_values=True)
        for to_ignore in self.ignorable_anchor:
            if to_ignore in qs:
                fragment = fragment.replace("{0}={1}".format(
                    to_ignore, qs[to_ignore][0]), '')

        u = urlparse.ParseResult(*u[:5], fragment=fragment)
        url = urlparse.urlunparse(u)
        return url

    def __urlencode(self, params):
        params = [i + ((params[i] != None) and ('=' + params[i]) or '')
            for i in params]
        return '&'.join(params)

    def clean_querystring(self, url=None):
        """Cleanup useless querystring parameter"""
        if not url:
            url = self.url

        u = urlparse.urlparse(url)
        qs = urlparse.parse_qs(u[4], keep_blank_values=True)
        new_qs = {}
        for k, v in qs.iteritems():
            if isinstance(v, (list, tuple)) and len(v) == 1 and not len(v[0]):
                v = None
            if not k in self.ignorable_qs:
                new_qs[k] = v

        u = u._replace(query=self.__urlencode(new_qs))
        url = urlparse.urlunparse(u)
        return url

    def clean(self, url=None):
        if not url:
            url = self.url
        url = self.clean_anchors(url)
        url = self.clean_querystring(url)
        return url


class LinkExtractor(object):
    """Extract usefull informations from a link"""

    def __init__(self, url):
        self.url = Link(url).clean()
        self.goose = Goose()
        self.raw_content = None
        self.full_content = None
        self.summary = None
        self.picture = None
        self.content_type = None
        self.status_code = None
        self.response = None

        self.title = None

    def fetch_url_content(self, url=None):
        """Fetches the content of the url"""
        if not url:
            url = self.url
        headers = {}

        url_parse = urlparse.urlparse(url)
        # quick hack: use our default useragent for some tiny urls sites
        # t.co have different behaviour, and legacy website may ban curl &
        # others
        if url_parse.netloc not in ('t.co', 'bit.ly'):
            headers['User-Agent'] = DEFAULT_USER_AGENT

        response = requests.get(url, headers=headers)
        self.url = url = response.url
        if response.status_code >= 400:
            raise index_exc.FetchException(
                u"Got a {0} status code while fetching {1}".format(
                    self.status_code, url))

        self.response = response

    def extract_text_html(self, page_content, url):
        article = self.goose.extractContent(url=url, rawHTML=page_content)
        self.full_content = article.cleanedArticleText
        if article.topImage:
            self.picture = article.topImage.imageSrc

        self.title = article.title
        self.summary = self.get_summary(article.cleanedArticleText)

    def extract_image_generic(self, page_content, url):
        url_parse = urlparse.urlparse(url)
        self.picture = url
        self.title = os.path.basename(url_parse.path)
        self.image = self.url
        self.content = ""
        self.full_content = ""
        # we don't want to store image in the database as blob.
        self.raw_content = ""
        self.summary = ""

    extract_image_jpeg = extract_image_png = extract_image_gif = extract_image_generic

    def extract(self, url=None):
        """Dispatch the resource extraction depending on the content_type"""
        if not url:
            url = self.url

        self.content_type = self.response.headers.get('content-type')
        self.status_code = self.response.status_code
        self.raw_content = self.response.content

        # parsing depending on content_type
        if self.content_type:
            method_name = self.content_type.split(';')[0]
            method_name = "extract_{0}".format(method_name.replace('/', '_'))
            if not hasattr(self, method_name):
                raise index_exc.UnsupportedContentType()
            getattr(self, method_name)(self.response.content, url)

        else:
            raise index_exc.ContentTypeNotFound

    def get_summary(self, text_content, max_length=500):
        """Extract a summary from a text"""
        offset = 0
        while offset < max_length:
            offset_tmp = text_content.find('.', offset + 1, max_length)
            if offset_tmp <= 0:
                break

            offset = offset_tmp

        return text_content[:offset + 1]
