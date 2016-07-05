import factory

from collectr.source import factories as source_factories

from .models import UserProfile


class UserProfileFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile

    user = factory.SubFactory(source_factories.UserFactory)
