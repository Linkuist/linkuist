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


from source.models import Collection, Filter, LinkSum

def link_match_filter(filtr, link):
    link_attr = getattr(link, filtr.field)
    if filtr.regexp in link_attr:
        return True

    try:
        if re.match(filtr.regexp, link_attr):
            return True
    except Exception, exc:
        print type(exc), "Exception error in %s for %s" % (link_attr, filtr.regexp)
        pass

    return False


def re_filter(username):
    filters = Filter.objects.select_related('collection').filter(user__username=username)
    links = LinkSum.objects.filter(user__username=username)
    all = Collection.objects.get(name__iexact="all", user__username=username)


    print filters
    print links

    for filtr in filters:
        qs_args = {
            "%s__iregex" % filtr.field : filtr.regexp,
            "user__username" : username
        }
        qs = LinkSum.objects.filter(**qs_args)
        if filtr.to_delete:
            qs.delete()
        else:
            qs.update(collection=filtr.to_collection)


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

def usage():
    print "Usage : %s <username>" % sys.argv[0]
    sys.exit()

def main():
    """some quick mains"""

    try:
        username = sys.argv[1]
    except IndexError:
        usage()

    re_filter(username)

if __name__ == '__main__':
    main()
