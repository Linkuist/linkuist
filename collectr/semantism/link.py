# -*- coding: utf-8 -*-
"""
    semantism tasks

"""
# python
import logging
import os
import pprint
import re
import string
import sys
import time
import traceback
import urllib
import urlparse

from cStringIO import StringIO

DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1 Iceweasel/9.0.1"

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
        self.ignorable_qs = ('utm_source', 'utm_medium', 'utm_campaign')
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
                fragment = fragment.replace("{0}={1}".format(to_ignore, qs[to_ignore][0]), '')

        u = urlparse.ParseResult(*u[:5], fragment=fragment)
        url = urlparse.urlunparse(u)
        return url

    def clean_querystring(self, url=None):
        """Cleanup useless querystring parameter"""
        if not url:
            url = self.url
        
        u = urlparse.urlparse(url)
        qs = urlparse.parse_qs(u[4], keep_blank_values=True)
        new_qs = dict((k, v) for k, v in qs.iteritems() if not k in self.ignorable_qs)

        u = u._replace(query=urllib.urlencode(new_qs, doseq=True))
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
        self.url = url
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
        if url_parse.netloc in ('t.co', 'bit.ly'):
            headers['User-Agent'] = DEFAULT_USER_AGENT

        response = requests.get(url, headers=headers)

        if response.status_code >= 400:
            raise index_exc.FetchException(
                u"Got a {0} status code while fetching {1}".format(self.status_code, url))

        self.response = response

    def extract_text_html(self, page_content, url):
        article = self.goose.extractContent(url=url, rawHTML=page_content)
        self.full_content = article.cleanedArticleText
        if article.topImage:
            self.picture = article.topImage.imageSrc

        self.title = article.title
        self.summary = self.get_summary(article.cleanedArticleText)

    def extract_image_generic(self, page_content, url):
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


    def get_summary(self, text_content, max_length=300):
        """Extract a summary from a text"""
        offset = 0
        while offset < max_length:
            offset_tmp = text_content.find('.', offset + 1, max_length)
            if offset_tmp <= 0:
                break

            offset = offset_tmp

        return text_content[:offset + 1]
