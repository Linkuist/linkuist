# -*- coding: utf-8 -*-
"""
    semantism tasks

"""
# python
import pprint
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
from collector.models import Filter, Collection, CollectionFilter
from source.models import Source, Origin, LinkSum

filters = Filter.objects.filter(user__username="benoit")
collection_filters = CollectionFilter.objects.values().all()

filtered_urls = dict()
for filtr in collection_filters:
    filtered_urls[filtr['base_url']] = [filtr['user_id'], filtr['collection_id']]


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
        if not hasattr(status, "text"):
            return False
        if "http://" not in status.text:
            return False
        if not 'urls' in status.entities:
            return False
        return True

    def find_collection(self, url):
        for key, value in filtered_urls.items():
            if key in url:
                return value[1]
        return None

    def find_language(self, raw_text):
        lang = self.lang_classifier.classify(raw_text)
        print lang
        return lang[0].split("--")[0]

    def run(self, status, user_id, post_date, author, *args, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("received status %d" %  user_id)
        if not self.is_valid(status):
            logger.info("status invalid and ignored")
            return
        for urls in status.entities['urls']:
            url = urls['url']
            if not url:
                continue
            try:
                lsum = LinkSum.objects.get(link=url, user__id=user_id)
                lsum.recommanded += 1
                lsum.save()
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


            summary = self.find_summary(article, logger, url)
            collection_id = None
            collection_id = self.find_collection(url)

            lang = self.find_language(article)
            interesting_words = filter_interesting_words(article, lang)
            tag_string = ",".join(interesting_words)
            logger.info("tags : %s" % tag_string)
            lsum = LinkSum.objects.create(
                tags=tag_string, summary=summary,
                title=title, link=url, collection_id=collection_id,
                read=False, recommanded=1,
                user_id=user_id, author=author,
            )

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
    if content.status_code < 400:
        html = content.text
        doc = Document(html)
        article = doc.summary()
        title = doc.short_title()
        url = content.url
        return title, article, url
    # hohai should raise an exception
    return None, None, None

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
