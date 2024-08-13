import datetime
import random
import string
from datetime import date, timedelta

import factory
import factory.fuzzy
from pydantic import BaseModel

from src.settings.enums import RegionEnum
from src.trips.dao import LocationDAO, RouteDAO, TripDAO
from tests.factories.base_factory import AsyncFactory


class TripFactory(AsyncFactory):
    class Meta:
        model = TripDAO

    name = factory.fuzzy.FuzzyText(length=10)
    description = factory.fuzzy.FuzzyText(length=100)
    region = factory.fuzzy.FuzzyChoice(RegionEnum)
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
    region: RegionEnum = random.choice([region.value for region in RegionEnum])
    date_from: date = (date.today() + timedelta(days=random.randint(5, 10))).isoformat()
    date_to: date = (date.today() + timedelta(days=random.randint(15, 25))).isoformat()


class LocationCreationFactory(BaseModel):
    name: str = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    description: str = "".join(random.choices(string.ascii_letters + string.digits, k=100))


class LocationFactory(AsyncFactory):
    class Meta:
        model = LocationDAO

    name = factory.fuzzy.FuzzyText(length=10)
    description = factory.fuzzy.FuzzyText(length=100)
    trip_id = None


class TripWith3LocationsFactory(TripFactory):
    memberhip1 = factory.RelatedFactory(LocationFactory, factory_related_name="locations")
    memberhip2 = factory.RelatedFactory(LocationFactory, factory_related_name="locations")
    memberhip3 = factory.RelatedFactory(LocationFactory, factory_related_name="locations")


class RouteFactory(AsyncFactory):
    class Meta:
        model = RouteDAO

    origin_id = None
    destination_id = None
    name = factory.fuzzy.FuzzyText(length=10)
    description = factory.fuzzy.FuzzyText(length=100)


class RouteCreationFactory(BaseModel):
    name: str = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    description: str = "".join(random.choices(string.ascii_letters + string.digits, k=100))
    origin_id: int = None
    destination_id: int = None
