import factory
import factory.fuzzy

from src.users.dao import UserDAO
from tests.factories.base_factory import AsyncFactory


class UserFactory(AsyncFactory):
    class Meta:
        model = UserDAO

    email = factory.Sequence(lambda n: f"user{n + 1}@triptip.pro")
    username = factory.fuzzy.FuzzyText(length=10)
    password = factory.fuzzy.FuzzyText(length=10)
    bio = factory.fuzzy.FuzzyText(length=100)
    userpic = factory.Sequence(lambda n: f"/media/userpics/user{n + 1}.png")
