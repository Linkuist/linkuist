
from tastypie.resources import ModelResource
from tastypie.authentication import MultiAuthentication, SessionAuthentication, ApiKeyAuthentication
from tastypie.authorization import Authorization

from source import models as source_models


class LinkSumResource(ModelResource):

    class Meta:
        queryset = source_models.LinkSum.objects.all()
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )

        resource_name = 'linksum'
        ordering = '-pk'

    def apply_authorization_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(user=request.user)

        return object_list.none()


class UrlResource(ModelResource):


    class Meta:
        queryset = source_models.Url.objects.all()
        excludes = ['raw_tags', 'content']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )
        resource_name = 'url'
        ordering = '-pk'

    def apply_authorization_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(linksum__user=request.user)

        return object_list.none()
