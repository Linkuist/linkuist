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

# celery
from celery.task import task, Task
from celery.task.sets import subtask
from celery.registry import tasks

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
        self.summary = None
        self.url = url
        self.logger = logger
        self.content = None
        self.status_code = None
        self.content_type = None

    def is_html_page(self):
        return 'html' in self.content_type

    def clean_url(self, url=None):
        import cgi
        import urlparse
        import urllib

        if not url:
            url = self.url

        u = urlparse.urlparse(url)
        qs = cgi.parse_qs(u[4])
        for key in qs:
            if key.startswith('utm_'):
                del qs[key]
        u = u._replace(query=urllib.urlencode(qs, True))
        url = urlparse.urlunparse(u)
        url = url.replace('#!', '?_escaped_fragment_=')
        self.logger.info("cleaned url : %s" % url)
        return url

    def find_url_language(self, summary=None):
        """Guess the content's language"""
        if not summary:
            summary = self.summary
        if not len(summary):
            self.lang = "en"
            return self.lang
        raw_text = summary[:]
        lang = self.lang_classifier.classify(raw_text)
        self.lang = lang[0].split("--")[0]
        self.logger.info("found lang : %s" % self.lang)
        return self.lang

    def find_url_summary(self, url=None):
        """resume the content of the link"""
        if not url:
            url = self.url

        article = self.summary[:]

        summary = ""
        try:
            tree = LH.fromstring(article)
            xpath_l = tree.xpath('//p/text()')
            summary = " ".join(xpath_l)
            summary = summary[:150]
        except Exception, exc:
            print traceback.print_exc()
            logger.error("no paragraph found in %s" % (url,))
            summary = ""
        if summary:
            summary = summary.strip()
        self.summary = summary
        self.logger.info("summary : %s" % summary)
        return summary

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
        self.content = content.text
        self.url = self.url_morph(content.url)
        url_parse = urlparse(url)

        if url_parse.netloc in oembed.keys():
            print "found oembed"
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

        elif "image" in self.content_type:
            self.summary = """<img src="%s" />""" % self.url
            self.title = self.url

        elif "html" in self.content_type:
            doc = Document(self.content)
            self.summary = doc.summary()
            try:
                self.title = doc.short_title()
            except AttributeError:
                self.title = u"No title"

        else:
            self.summary = None
            self.title = os.path.basename(url_parse.path)

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

class FakeLogger(object):

    def info(self, s):
        print s

class TwitterStatus(Task):
    """Specialised task for twitter statuses"""

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)

    def is_valid_url(self, status):
        if isinstance(status, basestring):
            if 'http://' or 'https://' in status:
                return [status]
        if not hasattr(status, "text"):
            return False
        if "http://" not in status.text:
            return False
        if not 'urls' in status.entities:
            return False
        urls = [d['url'] for d in status.entities['urls']]
        return urls

    def run(self, status, user_id, post_date, author, source, *args, **kwargs):
        logger = self.get_logger(**kwargs)
        user_id = int(user_id)
        self.filters = Filter.objects.filter(Q(user__pk=user_id) | Q(user__isnull=True))
        source = Source.objects.get(name__iexact=source)
        try:
            author, created = Author.objects.get_or_create(name=author, source=source)
        except Exception:
            author = Author.objects.get(name=author)
        default_collection = Collection.objects.get(name__iexact="all", user__isnull=True)
        urls = self.is_valid_url(status)
        if not urls:
            logger.info("status invalid and ignored")
            return

        logger.info("received valid status for user %d" %  user_id)

        for url in urls:
            if not url:
                continue

            url_parser = UrlParser(logger, url)

            try:
                url_parser.extract_url_content()
            except Exception, exc:
                import traceback
                print traceback.print_exc()
                logger.error("Can't extract title from %s (%s)" % (url, exc))
                return -1

            try:
                url_m = Url.objects.get(link=url_parser.url)
            except Url.DoesNotExist:
                uv = UrlViews.objects.create(count=0)
                try:
                    url_m = Url.objects.create(link=url_parser.url, views=uv,
                                               content=url_parser.summary)

                except Exception, exc:
                    url_m = Url.objects.get(link=url_parser.url)

            try:
                links_numb = LinkSum.objects.get(url__pk=url_m.pk, user__id=user_id)
                links_numb.recommanded += 1
                links_numb.save()
                logger.info("url already in database")
                continue
            except LinkSum.DoesNotExist:
                # link does not exist for now
                pass

            if url_parser.is_html_page():
                url_parser.find_url_summary()

                url_parser.find_url_language()

                tags = url_parser.find_tags()

                for tag in tags:
                    tag = tag.title()
                    try:
                        tag_m, created = Tag.objects.get_or_create(name=tag)
                    except Exception, e:
                        tag_m = Tag.objects.get(name=tag)
                    url_m.tags.add(tag_m)

                url_m.raw_tags = url_parser.tagstring
                url_m.save()
            else:
                tags = ""

            lsum = LinkSum(
                tags=url_parser.tagstring, summary=url_parser.summary, url=url_m,
                title=url_parser.title, link=url_parser.url, collection_id=default_collection.pk,
                read=False, recommanded=1, source=source,
                user_id=user_id, author=author,
            )

            try:
                filtr = url_parser.find_collection(lsum, self.filters)
                if filtr and filtr.xpath is not None and len(filtr.xpath.strip()) == 0:
                    filtr.xpath = None
                    filtr.save()
                if filtr and filtr.xpath is not None:
                    lsum.summary = url_parser.extract_link_xpath(filtr.xpath)
                    lsum.collection_id = filtr.to_collection_id
                    logger.info("new collection : %d" % filtr.to_collection_id)

            except DeleteLinkException:
                logger.info("Link not saved, filtered")
                return
            try:
                lsum.save()
            except Exception, exc:
                print exc
                lsum = LinkSum.objects.filter(url__pk=url_m.pk, user__id=user_id).update(recommanded=F('recommanded') + 1)



tasks.register(TwitterStatus)
