import os

import boto3
import pytest
from httpx import AsyncClient
from moto import mock_aws as aws
from sqlalchemy.ext.asyncio import AsyncSession

from src.settings.config import settings
from tests.factories.aws_config import mock_aio_aws
from tests.factories.trips_factories import (
    LocationFactory,
    RouteCreationFactory,
    RouteFactory,
    TripFactory,
)
from tests.factories.user_factories import UserFactory


@pytest.fixture(scope="function")
async def create_trip(session: AsyncSession, authenticated_ac: AsyncClient):
    trip = await TripFactory.create(db=session, author_id=authenticated_ac.user.awaitable_attrs.id)
    return trip


@pytest.fixture(scope="function")
async def create_trip_from_second_user(session: AsyncSession):
    user = await UserFactory.create(db=session)
    trip = await TripFactory.create(db=session, author_id=user.id)
    return trip


@pytest.fixture(scope="function")
async def create_route(session: AsyncSession, create_trip: TripFactory):
    trip = create_trip
    origin = await LocationFactory.create(db=session, trip_id=trip.id)
    destination = await LocationFactory.create(db=session, trip_id=trip.id)
    route = await RouteFactory.create(
        db=session, origin_id=origin.id, destination_id=destination.id, author_id=trip.author_id
    )
    return route


@pytest.fixture(scope="function")
async def create_location(session: AsyncSession, create_trip: TripFactory):
    trip = create_trip
    location = await LocationFactory.create(db=session, trip_id=trip.id)
    return location


@pytest.fixture(scope="function")
async def create_location_from_second_user(
    session: AsyncSession, create_trip_from_second_user: TripFactory
):
    trip = create_trip_from_second_user
    location = await LocationFactory.create(db=session, trip_id=trip.id)
    return location


@pytest.fixture(scope="function")
async def post_route_data(create_location: LocationFactory) -> tuple[dict, int]:
    origin = create_location
    destination = create_location
    data = RouteCreationFactory(origin_id=origin.id, destination_id=destination.id)
    data = data.model_dump()
    return data, origin.id


@pytest.fixture(scope="function")
async def post_route_data_for_others_location(
    create_location_from_second_user: LocationFactory,
) -> tuple[dict, int]:
    origin = create_location_from_second_user
    destination = create_location_from_second_user
    data = RouteCreationFactory(origin_id=origin.id, destination_id=destination.id)
    data = data.model_dump()
    return data, origin.id


@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_REGION"] = "us-east-1"
    settings.AWS_ACCESS_KEY_ID = "testing"
    settings.AWS_SECRET_ACCESS_KEY = "testing"
    settings.AWS_REGION = "us-east-1"


@pytest.fixture(scope="session")
async def mock_s3_bucket():
    with aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test_bucket")
        yield s3


@pytest.fixture()
def mock_aws(monkeypatch):
    """This fixture is needed for async compatibility of aioboto with moto."""
    with mock_aio_aws(monkeypatch):
        yield
