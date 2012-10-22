import factory

from django.contrib.webdesign import lorem_ipsum
from django.contrib.auth.models import User


import models as source_models

class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'username%s' % n)
    email = factory.Sequence(lambda n: 'user.name%s@example.com' % n)

class UrlViewsFactory(factory.Factory):
    FACTORY_FOR = source_models.UrlViews

    count = factory.Sequence(lambda n: int(n))

class SourceFactory(factory.Factory):
    FACTORY_FOR = source_models.Source

    name = factory.Sequence(lambda n: 'Source%s' % n)
    slug = factory.Sequence(lambda n: 'source%s' % n)

class OriginFactory(factory.Factory):
    FACTORY_FOR = source_models.Origin

    name = factory.Sequence(lambda n: 'Origin%s' % n)

class CollectionFactory(factory.Factory):
    FACTORY_FOR = source_models.Collection

    name = factory.Sequence(lambda n: 'Collection%s' % n)

class UrlFactory(factory.Factory):
    FACTORY_FOR = source_models.Url

    link = factory.Sequence(lambda n: 'http://this.is.link.%s.com/' % n)
    views = factory.SubFactory(UrlViewsFactory)
    #TODO
    #tags = models.ManyToManyField(Tag)
    raw_tags = factory.Sequence(lambda n: u",".join([lorem_ipsum.words(1) for x in range(0, 4)]))
    content = factory.Sequence(lambda n: lorem_ipsum.paragraph())

class AuthorFactory(factory.Factory):
    FACTORY_FOR = source_models.Author

    name = factory.Sequence(lambda n: 'Author%s' % n)
    source = factory.SubFactory(SourceFactory)

class LinkSumFactory(factory.Factory):
    FACTORY_FOR = source_models.LinkSum

    tags = factory.Sequence(lambda n: u",".join([lorem_ipsum.words(1) for x in range(0, 4)]))
    summary = factory.Sequence(lambda n: lorem_ipsum.paragraph())
    title = factory.Sequence(lambda n: lorem_ipsum.sentence())
    link = factory.Sequence(lambda n: 'http://this.is.link.%s.com/' % n)
    url = factory.SubFactory(UrlFactory)
    collection = factory.SubFactory(CollectionFactory)
    origin = factory.SubFactory(OriginFactory)
    source = factory.SubFactory(SourceFactory)
    user = factory.SubFactory(UserFactory)


    @classmethod
    def _prepare(cls, create, **kwargs):
        author = AuthorFactory()
        link = super(LinkSumFactory, cls)._prepare(create, **kwargs)
        link.authors.add(author)
        return link