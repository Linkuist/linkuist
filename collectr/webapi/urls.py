# django
from django.conf.urls.defaults import patterns, include, url

from tastypie.api import Api

from webapi import api

v1_api = Api(api_name='1.0')
v1_api.register(api.LinkSumResource())
v1_api.register(api.UrlResource())


urlpatterns = patterns('',
    (r'^', include(v1_api.urls)),
)
