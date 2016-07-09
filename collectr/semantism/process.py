# -*- coding: utf-8 -*-
"""
    Index an URL into collectr

"""


# python
import logging
import os
import re
import sys

sys.path.append('../')
sys.path.append('../../')

os.environ['DJANGO_SETTINGS_MODULE'] = 'collectr.settings'

# django
from django.db.models import Q

# collectr
from collectr.source.models import (Author, Source, LinkSum, Filter,
                           Collection, Url, UrlViews)

# semantism
from . import exceptions as index_exc
from . import oembed
from .link import LinkExtractor

logger = logging.getLogger('index_url')
logger.setLevel(logging.DEBUG)


def find_urls(content):
    if isinstance(content, basestring):
        if 'http://' or 'https://' in content:
            return [content]
    if not hasattr(content, "text"):
        return False
    if "http://" not in content.text:
        return False
    if not 'urls' in content.entities:
        return False
    urls = [d['url'] for d in content.entities['urls']]
    return urls


def update_from_oembed(url_object):
    result = oembed.resolve(url_object.link)
    if not result:
        logger.info(u"No oembed")
        return

    if result['type'] == 'photo':
        url_object.image = result['url']

    if result['type'] == 'video':
        if 'thumbnail_url' in result:
            url_object.image = result['thumbnail_url']

    if 'html' in result:
        url_object.html = result['html']

def create_url(link_extractor):
    url = None
    try:
        url = Url.objects.get(link=link_extractor.url)
        logger.info(u"Url already exists in database")
        return url
    except Url.DoesNotExist:
        pass

    uv = UrlViews.objects.create(count=0)

    url = Url(
        link=link_extractor.url, views=uv,
        summary=link_extractor.summary,
        content=link_extractor.full_content,
        image=link_extractor.picture,
        title=link_extractor.title)

    update_from_oembed(url)

    try:
        url.save()
    except Exception:
        logger.exception(u"Can't create the Url object")
        raise index_exc.UrlCreationException(u"Can't create the Url object")

    return url


def find_collection(linksum, filter_list):
    """Find the right collection for this link"""

    for filtr in filter_list:
        link_attr = getattr(linksum, filtr.field)
        if re.match(filtr.regexp, link_attr):
            if filtr.to_delete:
                raise index_exc.DeleteLinkException("Deleting link")
            linksum.collection_id = filtr.to_collection_id
            return filtr
    return None


def index_url(link, user_id, link_at, author_name, source_name):
    """Entry point to store our link & linksum into the database"""
    if not isinstance(user_id, (list, tuple)):
        user_id = [int(user_id)]

    default_collection = Collection.objects.get(name__iexact="all", user__isnull=True)

    urls = find_urls(link)
    if not urls:
        logger.info(u"No link provided")
        return

    #loads our filters
    filters = Filter.objects.filter(Q(user__pk__in=user_id) | Q(user__isnull=True))

    try:
        source = Source.objects.get(name__iexact=source_name)
    except Source.DoesNotExist:
        logger.info(u"source %s unknown" % source_name)
        return -1

    try:
        author = Author.objects.get(name=author_name)
    except Author.DoesNotExist:
        logger.info(u"Created author '{0}'".format(author_name))
        author, created = Author.objects.get_or_create(name=author_name, source=source)

    for url in urls:
        link_extractor = LinkExtractor(url)
        try:
            link_extractor.fetch_url_content()
        except index_exc.FetchException:
            logger.exception(u"Can't fetch link")
            continue

        try:
            link_extractor.extract()
        except Exception, exc:
            logger.warning(u"Can't extract url_content from %s" % url, exc_info=True)
            continue

        try:
            url_instance = create_url(link_extractor)
        except index_exc.UrlCreationException:
            logger.warning(u"can't create url for link {0}".format(url), exc_info=True)
            continue

        users_lsums = dict([(user, None) for user in user_id])
        for user in user_id:
            try:
                links_numb = LinkSum.objects.get(url=url_instance, user__id=user)
                links_numb.recommanded += 1
                links_numb.save()
                links_numb.authors.add(author)
                del users_lsums[user]
                logger.info(u"linksum already in database")

            except LinkSum.DoesNotExist:
                pass

        lsum = LinkSum(url=url_instance, collection_id=default_collection.pk,
                       read=False)

        try:
            find_collection(lsum, filters)

        except index_exc.DeleteLinkException:
            logger.info(u"Link not saved, filtered")
            continue

        for user in users_lsums:
            try:
                lsum.user_id = user
                lsum.save()
                lsum.authors.add(author)
                lsum.sources.add(source)
                for tags in url_instance.tags.all():
                    lsum.tags.add(tags)

            except Exception, exc:
                logger.exception(exc)
            logger.info(u"Added new link for user {0}".format(user_id))
        print lsum.url.pk
        print lsum.pk
