# django
from django.conf.urls import include, url

from tastypie.api import Api

from collectr.webapi import api

v1_api = Api(api_name='1.0')
v1_api.register(api.LinkSumResource())
v1_api.register(api.UrlResource())
v1_api.register(api.RssResource())
v1_api.register(api.CollectionResource())
v1_api.register(api.SourceResource())
v1_api.register(api.UserResource())


urlpatterns = [
    url(r'^', include(v1_api.urls)),
]
