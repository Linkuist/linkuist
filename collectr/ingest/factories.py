import factory
import factory.fuzzy

from collectr.source import models as source_factory

from . import models


class MediaFactory(factory.DjangoModelFactory):
    name = factory.Sequence("media-{}".format)
    kind = factory.fuzzy.FuzzyChoice(kind[0] for kind in models.Media.MEDIA_KINDS)

    class Meta:
        models = models.Media


class SharerFactory(factory.DjangoModelFactory):
    name = factory.Sequence("sharer-{}".format)
    media = factory.SubFactory(MediaFactory)

    class Meta:
        models = models.Sharer


class LinkFactory(factory.DjangoModelFactory):
    url = factory.Sequence("http://example.com/{}".format)
    hostname = 'http://example.com'

    class Meta:
        models = models.Link


class LinkMetadataFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(source_factory.UserFactory)
    link = factory.SubFactory(LinkFactory)
    sharer = factory.SubFactory(SharerFactory)

    class Meta:
        models = models.LinkMetadata
