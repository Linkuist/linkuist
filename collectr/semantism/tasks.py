# -*- coding: utf-8 -*-
"""
    semantism tasks

"""
# python
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

# collector
#from collector.models import Filter, Collection, CollectionFilter
from collector.exceptions import DeleteLinkException, UnsupportedContentException
from source.models import Source, Origin, LinkSum, Filter, Collection, Url, UrlViews, Tag

filters = Filter.objects.filter(user__username="benoit")
#collection_filters = CollectionFilter.objects.values().all()

filtered_urls = dict()
#for filtr in collection_filters:
#    filtered_urls[filtr['base_url']] = [filtr['user_id'], filtr['collection_id']]


"""
http://code.google.com/p/decruft/w/list
https://github.com/buriy/python-readability
http://stackoverflow.com/questions/4363899/making-moves-w-websockets-and-python-django-twisted
http://code.google.com/p/nltk/source/browse/trunk/nltk_contrib/nltk_contrib/misc/langid.py

"""

class ParsedUrl(object):
    def __init__(self):
        url = None
        summary = None
        html = None

class TwitterStatus(Task):

    def __init__(self, *args, **kwargs):
        print "instanciating task"
        super(Task, self).__init__(*args, **kwargs)
        self.lang_classifier = textcat.TextCat("/home/benoit/projs/collectr/collectr/fpdb.conf", "/usr/share/libtextcat/LM")

    def clean_url(self, url):
        import cgi
        import urlparse
        import urllib

        u = urlparse.urlparse(url)
        qs = cgi.parse_qs(u[4])
        for key in qs:
            if key.startswith('utm_'):
                del qs[key]
        u = u._replace(query=urllib.urlencode(qs, True))
        url = urlparse.urlunparse(u)
        return url

    def is_valid_url(self, status):
        if isinstance(status, unicode):
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

    def find_collection(self, lsum):
        for filtr in filters:
            link_attr = getattr(lsum, filtr.field)
            if re.match(filtr.regexp, link_attr):
                if filtr.to_delete:
                    raise DeleteLinkException("Deleting lonk")
                lsum.collection_id = filtr.to_collection_id
                return filtr

        return None

    def find_language(self, raw_text):
        lang = self.lang_classifier.classify(raw_text)
        return lang[0].split("--")[0]

    def run(self, status, user_id, post_date, author, *args, **kwargs):
        logger = self.get_logger(**kwargs)
        user_id = int(user_id)
        default_collection = Collection.objects.get(user__pk=user_id, name__iexact="all")
        urls = self.is_valid_url(status)
        if not urls:
            logger.info("status invalid and ignored")
            return
        logger.info("received status for user %d" %  user_id)
        for url in urls:
            url = self.clean_url(url)
            if not url:
                continue

            try:
                parsed_url = extract_url_content(url)
                url = parsed_url.url
                title = parsed_url.title

            except Exception, exc:
                import traceback
                print traceback.print_exc()
                logger.error("Can't extract title from %s (%s)" % (url, exc))
                return
            try:
                url_m = Url.objects.get(link=url)
            except Url.DoesNotExist:
                uv = UrlViews.objects.create(count=0)
                url_m = Url.objects.create(link=url, views=uv)

            try:
                lsum = LinkSum.objects.get(url__pk=url_m.pk, user__id=user_id)
                lsum.recommanded += 1
                lsum.save()
                logger.info("url already in database")
                continue
            except LinkSum.DoesNotExist:
                pass

            logger.info("extracted url : %s" % url)
            logger.info("extracted title : %s" % parsed_url.title)

            summary = self.find_summary(parsed_url.summary, logger, url)

            lang = self.find_language(parsed_url.summary)
            interesting_words = filter_interesting_words(parsed_url.summary, lang)
            tag_string = ",".join(interesting_words)
            logger.info("tags : %s" % tag_string)

            for tmp_tag in interesting_words:
                tag_m = Tag.objects.get_or_create(name=tmp_tag)
                url_m.tags.add(tag_m[0])

            url_m.raw_tags = tag_string
            url_m.save()
            url_m

            lsum = LinkSum(
                tags=tag_string, summary=summary, url=url_m,
                title=title, link=url, collection_id=default_collection.pk,
                read=False, recommanded=1,
                user_id=user_id, author=author,
            )
            try:
                if "instagr.am" in url:
                    print "Filter match"
                filtr = self.find_collection(lsum)
                if filtr and filtr.xpath is not None and len(filtr.xpath.strip()) == 0:
                    filtr.xpath = None
                    filtr.save()
                if filtr and filtr.xpath is not None:
                    lsum.summary = self.extract_link_xpath(filtr.xpath, parsed_url.content)
                    lsum.collection_id = filtr.to_collection_id

            except DeleteLinkException:
                logger.info("Link not saved, filtered")
                return
            lsum.save()

    def extract_link_xpath(self, xpath, article):
        try:
            doc = LH.fromstring(article)
            print doc
            print article
            print xpath
            result = doc.xpath(xpath)
            if isinstance(result, (list, tuple)):
                print result
                result = result[0]
            print LH.tostring(result)
            return LH.tostring(result)
        except Exception, exc:
            import traceback
            print traceback.print_exc()
            print "extract_link_xpath exc:", exc
            return ""

    def find_summary(self, article, logger, url):
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
        return summary

tasks.register(TwitterStatus)

@task
def extract_url_content(url, callback=None):
    parsed_url = ParsedUrl()
    url_parse = urlparse(url)
    headers = {}
    if url_parse.netloc != "t.co":
        user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1 Iceweasel/9.0.1"
        headers['User-Agent'] = user_agent
    content = requests.get(url, headers=headers)
    parsed_url.content_type = content.headers.get('content-type')
    parsed_url.status_code = content.status_code
    parsed_url.content = content.text
    parsed_url.url = content.url

    if content.status_code >= 400:
        raise Exception("Can't extract content for %s (http<%d>)" % (url, content.status_code))
    if "image" in parsed_url.content_type:
        parsed_url.summary = """<a href="%s>%s<a>""" % (url, url)
        parsed_url.title = url
        return parsed_url
    if "html" in parsed_url.content_type:
        html = content.text
        doc = Document(html)
        parsed_url.summary = doc.summary()
        parsed_url.title = doc.short_title()
        return parsed_url
    raise Exception("Can't extract content for %s" % url_parse.geturl())

@task
def tokenise(raw_text, callback=None):
    raw = nltk.clean_html(raw_text)
    tokens = nltk.wordpunct_tokenize(raw)
    return tokens
#    print tokens
#    tagged_words = nltk.pos_tag(tokens)
#    simplified = [(word, simplify_wsj_tag(tag)) for word, tag in tagged_words]
#    #print "sIMPLIFIED : ", simplified
#    return simplified


def filter_interesting_words(raw_text, lang):
    if lang == "fr":
        lang = "french"
    elif lang == "en":
        lang = "english"

    scorer = BigramAssocMeasures.likelihood_ratio
    compare_scorer = BigramAssocMeasures.raw_freq

    tokenised = tokenise(raw_text)
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
    return [' '.join(tup) for tup in cf.nbest(scorer, 15)]
