import factory
import factory.fuzzy

from src.users.models import User
from tests.factories.base_factory import BaseFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n + 1}@triptip.pro")
    username = factory.fuzzy.FuzzyText(length=10)
    password = factory.fuzzy.FuzzyText(length=10)
    bio = factory.fuzzy.FuzzyText(length=100)
    userpic = factory.Sequence(lambda n: f"/media/userpics/user{n + 1}.png")
