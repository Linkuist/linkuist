#!/usr/bin/env python

""" Adds RSS/Atom feeds to Linkuist. """

# python

# 3rd party
import feedparser

# django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

# collectr
from source.models import Rss


class Command(BaseCommand):
    args = '<url> <username>'
    help = 'Adds an RSS/Atom feed'

    def handle(self, *args, **kwargs):
        feed_url, username = args

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User {0} does not exist.'.format(username))

        feed = feedparser.parse(feed_url)

        obj, _ = Rss.objects.get_or_create(link=feed['href'],
                                           name=feed['feed']['title']
                                           )
        obj.users.add(user)
        obj.save()
