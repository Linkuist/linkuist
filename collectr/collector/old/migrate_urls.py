# -*- coding: utf-8 -*-
"""
    Script to Refilter links for a specified user.

"""
# python
import os
import re
import sys
import simplejson as json

# altering path to have access to django models
sys.path.append('../')
sys.path.append('../../')

os.environ['DJANGO_SETTINGS_MODULE'] ='collectr.settings'


from collectr import settings
from django.core.management import setup_environ
setup_environ(settings)


from source.models import Collection, Filter, LinkSum, Url, UrlViews, Tag


def migrate_links():
    links = LinkSum.objects.all()

    for link in links:
        print link.pk, ":", link.link
        url_m = Url.objects.get(link=link.link)
#        try:
#            url_m = Url.objects.get(link=link.link)
#        except Url.DoesNotExist:
#            view = UrlViews.objects.create()
#            tags = []
#            for tag in link.tags.split(','):
#                tmp_tag = Tag.objects.get_or_create(name=tag)
#                tags.append(tmp_tag[0])
#
#            url_m = Url.objects.create(
#                        link = link.link,
#                        views = view,
#                        raw_tags = link.tags
#                    )
#            for tag in tags:
#                url_m.tags.add(tag)
#            url_m.save()
        link.url = url_m
        link.save()


#    for link in links:
#        link_checked = False
#        for filtr in filters:
#            if link_match_filter(filtr, link):
#                if filtr.to_delete:
#                    #link.delete()
#                    print "deleting link %s" % link.link
#                else:
#                    print "moving link %s to %d" % (link.link, filtr.to_collection_id)
#                    link.collection_id = filtr.to_collection_id
#                    link.save
#                link_checked = True
#                break
#        if not link_checked:
#            print "moving link %s to all" % link.link
#            link.collection = all
#            link.save()


def main():
    """some quick mains"""

    migrate_links()

if __name__ == '__main__':
    main()
