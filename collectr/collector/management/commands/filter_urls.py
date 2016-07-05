# -*- coding: utf-8 -*-

"""Re-apply filters on links of specified user."""

# python
import json
import logging
import re

# django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

# collectr
from collectr.source.models import Collection, Filter, LinkSum


def re_filter(username):
    filters = Filter.objects \
        .select_related('collection') \
        .filter(user__username=username)
    links = LinkSum.objects.filter(user__username=username)

    for filtr in filters:
        qs_args = {
            '%s__iregex' % filtr.field: filtr.regex,
            'user__username': username,
        }
        qs = LinkSum.objects.filter(**qs_args)
        if filtr.to_delete:
            qs.delete()
        else:
            qs.update(collection=filtr.to_collection)


class Command(BaseCommand):
    args = '<user>'
    help = "re-apply user filters on his/her links"

    def handle(self, *args, **kwargs):
        username = args[0]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User {0} does not exist'.format(username))

        re_filter(username)

        self.stdout.write('User {0} links were re-filtered'.format(username))
