# -*- coding: utf-8 -*-
# python

# django
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# app

FILTERFIELDCHOICES = (
    ('tags', 'tags'),
    ('link', 'link'),
    ('summary', 'summary'),
    ('title', 'title'),
    ('content', 'content'),
    ('origin', 'origin'),
    ('source', 'source'),
    ('author', 'author'),
)


class Collection(models.Model):
    """A collection. Mostly the theme"""
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return "%s (%d)" % (self.name, self.user_id or 0)


class Filter(models.Model):
    """A filter for links. to delete them, or move them to a collection"""
    user = models.ForeignKey(User, null=True, blank=True)
    regexp = models.CharField(max_length=64)
    field = models.CharField(choices=FILTERFIELDCHOICES, max_length=32)
    to_delete = models.BooleanField(default=False)
    to_collection = models.ForeignKey(Collection, null=True, blank=True)
    xpath = models.TextField(null=True, blank=True)

    def __unicode__(self):
        if self.to_delete:
            return u"delete match %s (%d)" % (self.regexp, self.user_id or 0)
        return u"move match %s to %d (%d)" % (
            self.regexp, self.to_collection_id, self.user_id or 0)


class Source(models.Model):
    """A source, from where the link has been found"""
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=32, unique=True)

    def __unicode__(self):
        return self.name


class UrlViews(models.Model):
    """A denormalized field that count the number of view for a link"""
    count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Url View'
        verbose_name_plural = 'Url Views'

    def __unicode__(self):
        return u"%d" % self.count


class Tag(models.Model):
    """A tag"""
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class Url(models.Model):
    """An url"""
    link = models.TextField(unique=True)
    title = models.TextField()
    views = models.ForeignKey(UrlViews)
    tags = models.ManyToManyField(Tag)
    raw_tags = models.TextField()
    summary = models.TextField(null=True)
    html = models.TextField(null=True, blank=True)
    content = models.TextField()
    image = models.TextField(null=True, blank=True)
    inserted_at = models.DateTimeField(default=timezone.now)

    def create_tags(self, tags):
        """Sync’ tags & raw_tags"""
        for tag in tags:
            tag = tag.title()
            tag_instance, created = Tag.objects.get_or_create(name=tag)
            self.tags.add(tag_instance)

        self.raw_tags = u";".join(tags)

    def __unicode__(self):
        return self.link


class Author(models.Model):
    """A person that posted the link"""
    name = models.CharField(max_length=64, unique=True)
    source = models.ForeignKey(Source)


class LinkSum(models.Model):
    """A summary of the link.
    It's the user's part of the link, describing who posted the link,
    in which collection the link stays, it's origin ...
    """
    url = models.ForeignKey(Url, null=True, blank=True)
    read = models.BooleanField(default=False)
    recommanded = models.IntegerField(default=1)
    collection = models.ForeignKey(Collection, null=True)
    inserted_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User)
    sources = models.ManyToManyField(Source, null=True)
    tags = models.ManyToManyField(Tag)
    authors = models.ManyToManyField(Author, related_name="authors")
    hidden = models.BooleanField(default=False)

    class Meta:
        unique_together = ("url", "user")

    def __unicode__(self):
        if self.user_id and self.collection_id:
            return u'%s - user(%d) collection(%d)' % (
                self.url, self.user_id, self.collection_id)
        return u'%s' % self.url

    @property
    def link_tracking(self):
        return reverse('link_tracking:track_link', args=(self.pk,))

    @property
    def link(self):
        if self.url:
            return self.url.link
        return None

class HotTopic(models.Model):
    """A Hot Topic is when a subject comes more than once"""

    user = models.ForeignKey(User)
    sums = models.ManyToManyField(LinkSum)
    title = models.TextField()


class Rss(models.Model):
    """The simple RSS model"""
    link = models.URLField(verify_exists=False, max_length=1024, unique=True)
    name = models.CharField(max_length=128)
    users = models.ManyToManyField(User)
    etag = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = u'Rss'
        verbose_name_plural = u'Rss'

    def __unicode__(self):
        return self.name


class Reddit(models.Model):
    """Store the last post from reddit"""
    subreddit = models.CharField(max_length=128)
    users = models.ManyToManyField(User)
    uid = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = u'Reddit'
        verbose_name_plural = u'Reddits'

    def __unicode__(self):
        return self.subreddit
