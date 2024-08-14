from http import HTTPStatus

import pytest
from httpx import AsyncClient
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.trips.schemas import SDetailedTripOutput
from tests.factories.trips_factories import (
    LocationCreationFactory,
    LocationFactory,
    RouteFactory,
    TripCreationFactory,
    TripFactory,
)
from tests.factories.user_factories import UserFactory


class TestTrips:
    @pytest.mark.parametrize(
        "trip, status",
        [
            (TripCreationFactory(), HTTPStatus.CREATED),
            (TripCreationFactory(), HTTPStatus.BAD_REQUEST),
        ],
    )
    async def test_trip_creation(self, authenticated_ac: AsyncClient, trip: BaseModel, status):
        """
        Test trip creation endpoint.

        Create a trip and check if it appears on /trips endpoint.
        Creating trip with the same name twice should return 400.
        """
        trip_data = trip.model_dump()
        response = await authenticated_ac.post("/trips", json=trip_data)
        assert response.status_code == status
        if status == HTTPStatus.CREATED:
            assert response.json()["name"] == trip.name

    async def test_trip_creation_unauthenticated(self, ac: AsyncClient):
        """
        Test trip creation endpoint.

        Create a trip without authentication.
        """
        trip = TripCreationFactory()
        trip_data = trip.model_dump()
        response = await ac.post("/trips", json=trip_data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_trip_list(self, ac: AsyncClient, create_trip: TripFactory):
        """
        Test trips list endpoint.

        Create 10 trips and check if they appear on /trips endpoint.
        """
        trips = []
        for _ in range(10):
            trip = create_trip
            trips.append(trip.name)
        response = await ac.get("/trips")
        assert response.status_code == HTTPStatus.OK
        for trip in trips:
            assert any(response_trip["name"] == trip for response_trip in response.json())

    async def test_trip_detail(
        self, ac: AsyncClient, session: AsyncSession, create_trip: TripFactory
    ):
        """
        Test trip detail endpoint.

        Create a trip and check if it appears on /trips/{trip_id} endpoint.
        """
        trip = create_trip
        response = await ac.get(f"/trips/{trip.id}")
        assert response.status_code == HTTPStatus.OK
        assert response.json()["name"] == trip.name
        assert SDetailedTripOutput.model_validate(response.json())

    async def test_trip_detail_404(self, ac: AsyncClient):
        """
        Test trip detail endpoint for non-existent trip.

        Check if it returns a 404 error for a non-existent trip ID.
        """
        non_existent_id = 999
        response = await ac.get(f"/trips/{non_existent_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND

    async def test_location_creation(
        self, ac, authenticated_ac: AsyncClient, session: AsyncSession
    ):
        """
        Test location creation endpoint.

        Create a trip and add a location to it.
        1. Check location creation for an authenticated user.
        2. Check location creation for a user who is not the author of the trip.
        3. Check location creation for an anonymous user.s
        """

        async def test_loc(user_id, status, anonymous=False):
            trip = await TripFactory.create(db=session, author_id=user_id)
            location = LocationCreationFactory()
            location_data = location.model_dump()
            if anonymous:
                response = await ac.post(f"/trips/{trip.id}/locations", json=location_data)
            else:
                response = await authenticated_ac.post(
                    f"/trips/{trip.id}/locations", json=location_data
                )
            assert response.status_code == status
            if status == HTTPStatus.CREATED:
                assert response.json()["name"] == location.name

        await test_loc(authenticated_ac.user.awaitable_attrs.id, HTTPStatus.CREATED)
        user = await UserFactory.create(db=session)
        await test_loc(user.id, HTTPStatus.FORBIDDEN)
        await test_loc(user.id, HTTPStatus.UNAUTHORIZED, anonymous=True)

    async def test_get_locations(
        self, authenticated_ac: AsyncClient, session: AsyncSession, create_trip: TripFactory
    ):
        """
        Test get locations endpoint.

        Create a trip, add some locations to it,
         and check if the get locations endpoint returns them.
        """
        trip = create_trip
        for _ in range(3):
            await LocationFactory.create(db=session, trip_id=trip.id)
        response = await authenticated_ac.get(f"/trips/{trip.id}/locations")
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()) == 3

    async def test_trip_creation_with_fake_region(
        self, authenticated_ac: AsyncClient, session: AsyncSession
    ):
        """
        Test trip creation endpoint with fake region.

        Create a trip with a fake region and check if it returns a 422 error.
        """
        trip = TripCreationFactory()
        trip_data = trip.model_dump()
        trip_data["region"] = "Land of Sannikov"
        response = await authenticated_ac.post("/trips", json=trip_data)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    async def test_route_endpoint(
        self, authenticated_ac: AsyncClient, session: AsyncSession, create_route: RouteFactory
    ):
        """
        Test route endpoint.
        """
        route = create_route
        response = await authenticated_ac.get(f"/trips/locations/{route.origin_id}/route")
        assert response.status_code == HTTPStatus.OK
        assert response.json()["origin_id"] == route.origin_id
        assert response.json()["destination_id"] == route.destination_id


@pytest.mark.parametrize(
    "user_id, expected_status, anonymous",
    [
        ("authenticated_user", HTTPStatus.CREATED, False),
        ("other_user", HTTPStatus.FORBIDDEN, False),
        ("other_user", HTTPStatus.UNAUTHORIZED, True),
    ],
)
async def test_route_creation(
    ac,
    authenticated_ac: AsyncClient,
    session: AsyncSession,
    post_route_data: tuple[dict, int],
    post_route_data_for_others_location: tuple[dict, int],
    user_id,
    expected_status,
    anonymous,
):
    """
    Test route creation endpoint.

    Test cases:
    1. Check route creation for the authenticated user (author).
    2. Check route creation for a different authenticated user (non-author).
    3. Check route creation for an anonymous user.
    """
    if user_id == "authenticated_user":
        data, location = post_route_data
    else:
        data, location = post_route_data_for_others_location

    async def create_route():
        if anonymous:
            response = await ac.post(f"/trips/locations/{location}/route", json=data)
        else:
            response = await authenticated_ac.post(f"/trips/locations/{location}/route", json=data)
        return response

    if user_id == "authenticated_user":
        response = await create_route()
    else:
        other_user = await UserFactory.create(db=session)
        authenticated_ac.user = other_user
        response = await create_route()

    assert response.status_code == expected_status
    if expected_status == HTTPStatus.CREATED:
        assert response.json()["name"] == data["name"]
