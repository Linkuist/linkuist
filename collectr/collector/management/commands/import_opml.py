#!/usr/bin/env python
"""
    Parse opml files (only test from google reader)

"""

import logging
from collections import defaultdict

# 3rd party
import opml

# django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

# collectr
from source.models import Rss

logger = logging.getLogger(__name__)


def parse_outline(outline, user, stats):
    if len(outline):
        for o in outline:
            parse_outline(o, user, stats)

    if getattr(outline, "type", "notype") == "rss":
        rss, created = Rss.objects.get_or_create(link=outline.url,
                                                 name=outline.text)
        rss.users.add(user)
        rss.save()
        if created:
            stats['created'] += 1
        else:
            stats['existing'] += 1
        logger.info("%s added for user %s", outline.url, user.username)


class Command(BaseCommand):
    args = '<url> <username>'
    help = 'Imports Atom/RSS feeds from OPML file'

    def handle(self, *args, **kwargs):
        opml_file, username = args

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User {0} does not exist'.format(username))

        stats = defaultdict(int)
        outlines = opml.parse(opml_file)
        for outline in outlines:
            parse_outline(outline, user, stats)

        self.stdout.write(
            'Imported %d new feeds from %s (%d already present)' %
            (stats['created'], opml_file, stats['existing'])
        )
