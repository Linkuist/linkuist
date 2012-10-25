import factory

import source.factories as source_factories

class UserProfileFactory(factory.Factory):
    FACTORY_FOR = UserProfile

    user = factory.SubFactory(source_factories.UserFactory)
