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


from source.models import Collection, Filter, LinkSum, Url, UrlViews, Tag, Author, Source


def migrate_links_to_author():
    links = LinkSum.objects.all()
    source = Source.objects.get(name__iexact="twitter")

    for link in links:
        print link.pk, ":", link.link
        author, created = Author.objects.get_or_create(name=link.old_author, source=source)
        link.author = author
        link.save()


def main():
    """some quick mains"""

    migrate_links_to_author()

if __name__ == '__main__':
    main()
