# python
from urlparse import urlparse
from datetime import datetime

# django
from django.db import models
from django.contrib.auth.models import User

# app
from collector.models import Collection

class Source(models.Model):
    name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

class Origin(models.Model):
    name = models.CharField(max_length=128)

class LinkSum(models.Model):
    tags = models.TextField()
    summary = models.TextField(null=True)
    title = models.TextField()
    link = models.TextField()
    origin = models.ForeignKey(Origin, null=True)
    source = models.ForeignKey(Source, null=True)
    read = models.BooleanField(default=False)
    recommanded = models.IntegerField(default=1)
    collection = models.ForeignKey(Collection, null=True)
    inserted_at = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(User)
    author = models.CharField(max_length=64)

    def reco(self):
        return """%d""" % self.recommanded
    reco.short_description = "Reco"

    def link_title(self):
        return """<a href="%s" target="_blank">%s</a>""" % (self.link, self.title)
    link_title.short_description = "Title"
    link_title.allow_tags = True

    def get_tags(self):
        if self.tags:
            return self.tags.split(',')
        return []
