# django
from django.conf.urls.defaults import patterns, include

from tastypie.api import Api

from webapi import api

v1_api = Api(api_name='1.0')
v1_api.register(api.LinkSumResource())
v1_api.register(api.UrlResource())
v1_api.register(api.RssResource())
v1_api.register(api.CollectionResource())
v1_api.register(api.SourceResource())
v1_api.register(api.UserResource())


urlpatterns = patterns('',
    (r'^', include(v1_api.urls)),
)
