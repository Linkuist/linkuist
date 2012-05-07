# python
from datetime import datetime

# django
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

#class Filter(models.Model):
#    filter = models.CharField(_(u'filter'), max_length=128)
#    user = models.ForeignKey(User)
#    does_it_contain = models.BooleanField(default=True)
#
#
#class Author(models.Model):
#    name = models.CharField(max_length=128)
#    type = models.ForeignKey('CollectionItemType')
#
#class CollectionItemType(models.Model):
#    type = models.CharField(_(u'type'), max_length=32)
#
#    def __unicode__(self):
#        return self.type
#
#class CollectionFilter(models.Model):
#    collection = models.ForeignKey('Collection')
#    user = models.ForeignKey(User)
#    base_url = models.CharField(max_length=128)
#
#
#class CollectionItem(models.Model):
#    direct_link = models.TextField()
#    type = models.ForeignKey(CollectionItemType)
#    date = models.DateTimeField(default=datetime.now)
#    summary = models.TextField()
#    picture = models.TextField()
#    is_read = models.BooleanField(default=False)
#    author = models.ForeignKey(Author)
#    def __unicode__(self):
#        return self.direct_link
#
#class Collection(models.Model):
#    name = models.CharField(_(u'Collection name'), max_length=128)
#    user = models.ForeignKey(User)
#
#    def __unicode__(self):
#        return self.name
