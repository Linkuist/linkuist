import factory

from django.contrib.webdesign import lorem_ipsum
from django.contrib.auth.models import User

from . import models


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'username%s' % n)
    email = factory.Sequence(lambda n: 'user.name%s@example.com' % n)
    password = factory.PostGenerationMethodCall('set_password', '')


class UrlViewsFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.UrlViews

    count = factory.Sequence(lambda n: int(n))


class SourceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Source

    name = factory.Sequence(lambda n: 'Source%s' % n)
    slug = factory.Sequence(lambda n: 'source%s' % n)


class CollectionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Collection

    name = factory.Sequence(lambda n: 'Collection%s' % n)


class FilterFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Filter

    to_collection = factory.SubFactory(CollectionFactory)


class AuthorFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Author

    name = factory.Sequence(lambda n: 'Author%s' % n)
    source = factory.SubFactory(SourceFactory)


class UrlFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Url

    link = factory.Sequence(lambda n: 'http://this.is.link.%s.com/' % n)
    title = factory.Sequence(lambda n: lorem_ipsum.sentence())
    views = factory.SubFactory(UrlViewsFactory)
    #TODO
    #tags = models.ManyToManyField(Tag)
    raw_tags = factory.Sequence(lambda n: u",".join([lorem_ipsum.words(1) for x in range(0, 4)]))
    summary = factory.Sequence(lambda n: lorem_ipsum.paragraph())
    content = factory.Sequence(lambda n: lorem_ipsum.paragraph())


class LinkSumFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.LinkSum

    url = factory.SubFactory(UrlFactory)
    collection = factory.SubFactory(CollectionFactory)
    user = factory.SubFactory(UserFactory)
    #source = factory.SubFactory(SourceFactory)

    @classmethod
    def _prepare(cls, create, **kwargs):
        author = AuthorFactory()
        link = super(LinkSumFactory, cls)._prepare(create, **kwargs)
        link.authors.add(author)
        return link


class RssFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Rss

    link = factory.Sequence(lambda n: u"http://this.is.a.rss-feed-%s.com/" % n)
    name = factory.Sequence(lambda n: u"Rss feed #%s" % n)
