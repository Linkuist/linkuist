#!/usr/bin/env python
"""
    Parse opml files (only test from google reader)

"""

import logging

# 3rd party
import opml

# django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

# collectr
from source.models import Rss

logger = logging.getLogger(__name__)


def parse_outline(outline, user):
    if hasattr(outline, "title"):
        for o in outline._outlines:
            parse_outline(o, user)
    if hasattr(outline, "type") and outline.type == "rss":
        rss, created = Rss.objects.get_or_create(link=outline.xmlUrl,
                name=outline.title)
        rss.users.add(user)
        rss.save()
        logger.info("%s added for user %s", outline.xmlUrl, user.username)


class Command(BaseCommand):
    args = '<url> <username>'
    help = 'Imports Atom/RSS feeds from OPML file'

    def handle(self, *args, **kwargs):
        opml_file, username = args

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User {0} does not exist'.format(username))

        outlines = opml.parse(opml_file)
        for outline in outlines:
            parse_outline(outline, user)
