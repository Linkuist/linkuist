# -*- coding: utf-8 -*-
"""
    semantism tasks

"""
# python
import os
import pprint
import re
import string
import sys
import time
import traceback

from cStringIO import StringIO
from urlparse import urlparse
from lxml import etree
import lxml.html as LH


# 3rd nltk
import nltk
from nltk.corpus import stopwords, webtext
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, spearman_correlation, ranks_from_scores
from nltk.tag.simplify import simplify_wsj_tag

# 3rd party
import requests
import textcat

from readability.readability import Document

# django
from django.db.models import Q, F

# collector
try:
    from semantism.embed import oembed
except Exception, exc:
    oembed = {}
from semantism.exceptions import (DeleteLinkException, UnsupportedContentException,
                                  UrlExtractException)

from source.models import (Author, Source, Origin, LinkSum, Filter,
                           Collection, Url, UrlViews, Tag)


"""
http://code.google.com/p/decruft/w/list
https://github.com/buriy/python-readability
http://stackoverflow.com/questions/4363899/making-moves-w-websockets-and-python-django-twisted
http://code.google.com/p/nltk/source/browse/trunk/nltk_contrib/nltk_contrib/misc/langid.py

"""

class UrlParser(object):
    """Parse our url"""

    def __init__(self, logger, url):
        self.lang_classifier = textcat.TextCat("/home/benoit/projs/collectr/collectr/fpdb.conf", "/usr/share/libtextcat/LM")
        self.tags = []
        self.tagstring = None
        self.title = []
        self.image = None
        self.summary = None
        self.url = url
        self.logger = logger
        self.content = None
        self.status_code = None
        self.content_type = None

    def is_html_page(self):
        return 'html' in self.content_type

    def is_image(self):
        return 'image' in self.content_type

    def is_valid_url(self, url=None):
        if not url:
            url = self.url

    def clean_url(self, url=None):
        import cgi
        import urlparse
        import urllib

        if not url:
            url = self.url

        u = urlparse.urlparse(url)
        qs = cgi.parse_qs(u[4])
        qs = dict((k, v) for k, v in qs.iteritems() if not k.startswith('utm_'))
        u = u._replace(query=urllib.urlencode(qs, True))
        url = urlparse.urlunparse(u)
        url = url.replace('#!', '?_escaped_fragment_=')
        self.logger.info("cleaned url : %s" % url)
        return url

    def find_url_language(self, summary=None):
        """Guess the content's language"""
        if not summary:
            summary = self.summary

        raw_text = summary[:]
        try:
            lang = self.lang_classifier.classify(raw_text)
            self.lang = lang[0].split("--")[0]
            self.logger.info("found lang : %s" % self.lang)
        except Exception, exc:
            self.logger.warning("Can't find document lang, fallback to english")
            self.lang = "en"
        return self.lang

    def find_url_summary(self, url=None):
        """resume the content of the link"""
        if not url:
            url = self.url

        article = self.summary[:]

        if 'html' in self.content_type:
            summary = ""
            try:
                tree = LH.fromstring(article)
                xpath_l = tree.xpath('//p/text()')
                summary = " ".join(xpath_l)
            except Exception, exc:
                print traceback.print_exc()
                logger.error("no paragraph found in %s" % (url,))
                summary = ""
            if summary:
                summary = summary.split('.')
                summary = filter(len, summary)
                summary = ". ".join(summary[:3])
                summary += "."
                if len(summary) > 600:
                    summary[:500]
            self.summary = summary
        self.logger.info("summary : %s" % self.summary)
        return self.summary

    def find_collection(self, linksum, filtrs):
        """Find the right collection for this link"""

        for filtr in filtrs:
            link_attr = getattr(linksum, filtr.field)
            if re.match(filtr.regexp, link_attr):
                if filtr.to_delete:
                    raise DeleteLinkException("Deleting link")
                linksum.collection_id = filtr.to_collection_id
                return filtr
        return None

    def find_tags(self, summary=None, lang=None):
        if not summary:
            summary = self.content
        if not lang:
            lang = self.lang

        raw_text = summary[:]
        if lang == "fr":
            lang = "french"
        elif lang == "en":
            lang = "english"

        scorer = BigramAssocMeasures.likelihood_ratio
        compare_scorer = BigramAssocMeasures.raw_freq

        tokenised = self.tokenise(raw_text)
        ignored_words = stopwords.words(lang)
        word_filter = lambda w: len(w) < 3 or w.lower() in ignored_words
        cf = BigramCollocationFinder.from_words(tokenised)
        cf.apply_freq_filter(3)
        cf.apply_word_filter(word_filter)

    #    print '\t', [' '.join(tup) for tup in cf.nbest(scorer, 15)]
    #    print '\t Correlation to %s: %0.4f' % (compare_scorer.__name__,
    #                spearman_correlation(
    #                ranks_from_scores(cf.score_ngrams(scorer)),
    #                ranks_from_scores(cf.score_ngrams(compare_scorer))))
        self.tags = [' '.join(tup) for tup in cf.nbest(scorer, 15)]
        punctuation = set(string.punctuation)
        tags = []

        def has_punctuation(tag):
            for c in string.punctuation:
                if c in tag:
                    return True

            return False

        for tag in self.tags:
            tag = tag.title()
            if not has_punctuation(tag):
                tags.append(tag)
        self.tags = tags
        self.tagstring = ",".join(self.tags)
        return self.tags

    def url_morph(self, url):
        if url.startswith('http://twitpic.com/'):
            url = re.sub("http://twitpic.com/([a-zA-Z0-9]*)", lambda x: "http://twitpic.com/show/full/%s.jpg" % x.group(1), url)
        return url

    def extract_url_content(self, url=None):
        if not url:
            url = self.url
        url_parse = urlparse(url)
        headers = {}
        if url_parse.netloc != "t.co":
            user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1 Iceweasel/9.0.1"
            headers['User-Agent'] = user_agent

        content = requests.get(url, headers=headers)
        self.content_type = content.headers.get('content-type')
        self.status_code = content.status_code
        self.url = self.url_morph(content.url)
        self.url = self.clean_url(self.url)
        self.url_parse = urlparse(self.url)

        if url_parse.netloc in oembed.keys():
            self.logger.debug("found oembed")
            mod = oembed[url_parse.netloc]
            self.content = mod.get_widget(url)
            self.summary = self.content
            self.title = os.path.basename(url_parse.path)
            self.content_type = "collectr/parsed"
            self.tags = [mod.get_tag()]
            self.tagstring = mod.get_tag()
            return

        if self.status_code >= 400:
            raise UrlExtractException("Can't extract content for %s (http<%d>)" % (url, content.status_code))

        elif self.is_image():
            self.logger.debug("log: content type : image")
            self.title = os.path.basename(url_parse.path)
            self.image = self.url
            self.content = ""
            self.summary = ""

        elif self.is_html_page():
            self.content = content.text
            self.image = self.find_taller_image(self.content)
            doc = Document(self.content)
            self.summary = doc.summary()
            try:
                self.title = doc.short_title()
            except AttributeError:
                self.title = u"No title"


        else:
            self.summary = None
            self.title = os.path.basename(url_parse.path)

        if self.image:
            self.logger.info("found image : %s"%self.image)
        self.logger.info("Content-Type: %s" % self.content_type)

    def extract_link_xpath(self, xpath):
        try:
            doc = LH.fromstring(self.content)
            result = doc.xpath(xpath)
            if isinstance(result, (list, tuple)):
                result = result[0]
            for attr in ('style', 'border', 'height', 'width'):
                try:
                    del result.attrib[attr]
                except KeyError:
                    pass
            self.summary = LH.tostring(result)
            self.logger.info("extracted xpath content: %s" % self.summary)
        except Exception, exc:
            import traceback
            print traceback.print_exc()
            print "extract_link_xpath exc:", exc
            return ""
        return self.summary

    def as_linksum(self):
        """Return a linksum objet"""
        pass

    def tokenise(self, raw_text, callback=None):
        raw = nltk.clean_html(raw_text)
        tokens = nltk.wordpunct_tokenize(raw)
        return tokens

    def find_taller_image(self, page_content):
        best_perimeter = 0
        found_image = None
        if not page_content or len(page_content) <= 0:
            self.logger.warning("Page has no content")
            return found_image
        tree = LH.fromstring(page_content)
        image_list = tree.xpath("//img")

        for image in image_list:
            width = image.get('width')
            height = image.get('height')
            if width and height:
                try:
                    width = int(width)
                    height = int(height)
                except ValueError:
                    continue
                perimeter = width * height
                if perimeter > best_perimeter:
                    best_perimeter = perimeter
                    found_image = image.get('src')

        if found_image and found_image.startswith('/'):
            url_parse = urlparse(self.url)
            found_image = "%s://%s%s" % (url_parse.scheme,
                    url_parse.netloc, found_image)
        elif found_image and not found_image.startswith('http'):
            # this is a relative path to the image
            url_parse = urlparse(self.url)
            found_image = "%s://%s%s%s" % (url_parse.scheme, url_parse.netloc,
                    url_parse.path, found_image)

            return found_image
