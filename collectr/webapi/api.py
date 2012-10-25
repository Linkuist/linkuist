
from tastypie.resources import ModelResource
from source import models as source_models


class LinkSumResource(ModelResource):

    class Meta:
        queryset = source_models.LinkSum.objects.all()
        resource_name = 'linksum'

class UrlResource(ModelResource):

    class Meta:
        queryset = source_models.Url.objects.all()
        resource_name = 'url'