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
from lxml import etree
from urlparse import urlparse

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
default_collection = Collection.objects.get(user__username="benoit", name__iexact="all")
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
class TwitterStatus(Task):

    def __init__(self, *args, **kwargs):
        print "instanciating task"
        super(Task, self).__init__(*args, **kwargs)
        self.lang_classifier = textcat.TextCat("/home/benoit/projs/collectr/collectr/fpdb.conf", "/usr/share/libtextcat/LM")

    def is_valid(self, status):
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
                break

    def find_language(self, raw_text):
        lang = self.lang_classifier.classify(raw_text)
        print lang
        return lang[0].split("--")[0]

    def run(self, status, user_id, post_date, author, *args, **kwargs):
        user_id = int(user_id)
        logger = self.get_logger(**kwargs)
        logger.info("received status %d" %  user_id)
        urls = self.is_valid(status)
        if not urls:
            logger.info("status invalid and ignored")
            return
        for url in urls:
            print "url to blah : ", url
            if not url:
                continue

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
            try:
                title, article, url = extract_url_content(url)
            except Exception, exc:
                import traceback
                print traceback.print_exc()
                logger.error("Can't extract title from %s (%s)" % (url, exc))
                return

            logger.info("extracted url : %s" % url)
            logger.info("extracted title : %s" % title)

            print "url : ", url
            summary = self.find_summary(article, logger, url)

            lang = self.find_language(article)
            interesting_words = filter_interesting_words(article, lang)
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
                collection_id = self.find_collection(lsum)
            except DeleteLinkException:
                logger.info("Link not saved, filtered")
                return
            if collection_id:
                lsum.collection = collection_id
            lsum.save()
    
    def find_summary(self, article, logger, url):
        pouet = ""
        try:
            tree = etree.fromstring(article)
            xpath_l = tree.xpath('//p[1]')[0].text
            pouet = xpath_l[0]
            try:
                if len(pouet) < 50:
                    pouet = tree.xpath('//p[1]')[0].text
                    pouet += xpath_l[1]
            except Exception, exc:
                pass
            logger.info("paragraph : %s" % pouet)
        except Exception, exc:
            print traceback.print_exc()
            logger.error("no paragraph found in %s" % (url,))
            pouet = None
        if pouet:
            pouet = pouet.strip()
        return pouet

tasks.register(TwitterStatus)

@task
def extract_url_content(url, callback=None):
    url_parse = urlparse(url)
    headers = {}
    if url_parse.netloc != "t.co":
        user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1 Iceweasel/9.0.1"
        headers['User-Agent'] = user_agent
    content = requests.get(url, headers=headers)
    content_type = content.headers.get('content-type')
    if not "html" in content_type:
        raise Exception("unsupported content_type %s" % content_type)
    print 'content-type:', content.headers.get('content-type')
    print content.headers
    if content.status_code < 400:
        html = content.text
        doc = Document(html)
        article = doc.summary()
        title = doc.short_title()
        url = content.url
        return title, article, url
    else:
        print content
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
