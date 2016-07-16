from django.contrib.auth import models as auth_models
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

from django.utils.translation import ugettext_lazy as _


class Media(models.Model):

    MEDIA_KINDS = (
        ('bookmark', _('Bookmark')),
        ('irc', _('IRC')),
        ('rss', _('RSS Feed')),
        ('social-network', _('social network')),
    )

    name = models.TextField()
    kind = models.CharField(max_length=64, choices=MEDIA_KINDS)


class Sharer(models.Model):
    """The person who shared the link.

    For instance the twitter username.
    """
    name = models.TextField()
    data = JSONField(null=True, blank=True)
    media = models.ForeignKey(Media)

    class Meta:
        unique_together = ('name', 'media')


class Link(models.Model):
    url = models.TextField()
    hostname = models.TextField()

    published_at = models.DateTimeField(default=timezone.now)


class LinkMetadata(models.Model):
    user = models.ForeignKey(auth_models.User)
    link = models.ForeignKey(Link, related_name='metadata')
    sharer = models.ForeignKey(Sharer)

    received_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(default=timezone.now)
