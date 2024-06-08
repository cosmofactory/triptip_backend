import datetime
import random
import string
from datetime import date, timedelta

import factory
import factory.fuzzy
from pydantic import BaseModel

from src.trips.models import Location, Trip
from tests.factories.base_factory import BaseFactory


class TripFactory(BaseFactory):
    class Meta:
        model = Trip

    name = factory.fuzzy.FuzzyText(length=10)
    description = factory.fuzzy.FuzzyText(length=100)
    date_from = factory.fuzzy.FuzzyDate(
        datetime.date.today() + datetime.timedelta(days=5),
        datetime.date.today() + datetime.timedelta(days=10),
    )
    date_to = factory.fuzzy.FuzzyDate(
        datetime.date.today() + datetime.timedelta(days=15),
        datetime.date.today() + datetime.timedelta(days=25),
    )
    author_id = None


class TripCreationFactory(BaseModel):
    name: str = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    description: str = "".join(random.choices(string.ascii_letters + string.digits, k=100))
    date_from: date = (date.today() + timedelta(days=random.randint(5, 10))).isoformat()
    date_to: date = (date.today() + timedelta(days=random.randint(15, 25))).isoformat()


class LocationCreationFactory(BaseModel):
    name: str = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    description: str = "".join(random.choices(string.ascii_letters + string.digits, k=100))


class LocationFactory(BaseFactory):
    class Meta:
        model = Location

    name = factory.fuzzy.FuzzyText(length=10)
    description = factory.fuzzy.FuzzyText(length=100)
    trip_id = factory.SubFactory(TripFactory)


class TripWith3LocationsFactory(TripFactory):
    memberhip1 = factory.RelatedFactory(LocationFactory, factory_related_name="locations")
    memberhip2 = factory.RelatedFactory(LocationFactory, factory_related_name="locations")
    memberhip3 = factory.RelatedFactory(LocationFactory, factory_related_name="locations")
