# django
from django.conf.urls import url
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q



from tastypie import fields
from tastypie.authentication import (MultiAuthentication,
                                     SessionAuthentication,
                                     ApiKeyAuthentication)

from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash

from collectr.source import models as source_models


class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'auth/user'
        excludes = ['email', 'password', 'is_superuser']

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/signin%s$" % (self._meta.resource_name, trailing_slash()),
            self.wrap_view('signin'), name="api_signin"),
        ]

    def signin(self, request, **kwargs):
        try:
            self.method_check(request, allowed=['post'])

            # Per https://docs.djangoproject.com/en/1.3/topics/auth/#django.contrib.auth.login...
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return self.create_response(request, {'success': True})
                else:
                    # Return a 'disabled account' error message
                    return self.create_response(request, {'success': False})
            else:
                # Return an 'invalid login' error message.
                return self.create_response(request, {'success': False})
        except Exception, e:
            print e

class UrlResource(ModelResource):

    class Meta:
        queryset = source_models.Url.objects.all()
        excludes = ['raw_tags', 'content']
        authentication = MultiAuthentication(
            ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )
        resource_name = 'url'
        ordering = ['-pk']

    def apply_authorization_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(
                linksum__user=request.user).order_by('-pk')

        return object_list.none()


class TagResource(ModelResource):

    class Meta:
        queryset = source_models.Tag.objects.all()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )

        resource_name = 'tag'
        ordering = ['pk']
        exclude = ['slug']


class AuthorResource(ModelResource):

    class Meta:
        queryset = source_models.Author.objects.all()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )

        resource_name = 'author'
        ordering = ['-pk']


class CollectionResource(ModelResource):

    class Meta:
        queryset = source_models.Collection.objects.all()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )

        resource_name = 'collection'
        ordering = ['pk']
        exclude = ['user']
        filtering = {"name": [ "exact", "in" ] }

    def apply_authorization_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(Q(user=request.user) | Q(user__isnull=True))
        return object_list.none()


class LinkSumResource(ModelResource):

    url = fields.ToOneField(UrlResource, 'url', full=True)
    authors = fields.ToManyField(AuthorResource, 'authors', full=True)
    tags = fields.ToManyField(TagResource, 'tags', full=True)
    link_tracking = fields.CharField(attribute='link_tracking')
    collection = fields.ToOneField(CollectionResource, 'collection', full=True)

    class Meta:
        queryset = source_models.LinkSum.objects.all()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )
        filtering = {
            'collection': ALL_WITH_RELATIONS,
        }

        resource_name = 'linksum'
        ordering = ['-pk']

    def apply_authorization_limits(self, request, object_list):
        if request and request.user.is_authenticated():
            return object_list.select_related('url').filter(
                user=request.user).order_by('-pk')
        return object_list.none()


class FilterResource(ModelResource):

    class Meta:
        queryset = source_models.Filter.objects.all()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )

        resource_name = 'filter'
        ordering = ['pk']
        exclude = ['user']

    def apply_authorization_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(user=request.user)
        return object_list.none()


class SourceResource(ModelResource):

    class Meta:
        queryset = source_models.Source.objects.all()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )

        resource_name = 'source'
        ordering = ['pk']
        exclude = ['slug']


class RssResource(ModelResource):

    class Meta:
        queryset = source_models.Rss.objects.all()
        authentication = MultiAuthentication(
            ApiKeyAuthentication(), SessionAuthentication())
        authorization = (
            Authorization()
        )

        resource_name = 'rss'
        ordering = ['pk']
        exclude = ['uers']

    def apply_authorization_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(users=request.user)
        return object_list.none()
