from http import HTTPStatus

import pytest
from httpx import AsyncClient
from pydantic import BaseModel

from src.trips.schemas import SDetailedTripOutput
from tests.factories.trips_factories import (
    LocationCreationFactory,
    LocationFactory,
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

    async def test_trip_list(self, ac: AsyncClient):
        """
        Test trips list endpoint.

        Create 10 trips and check if they appear on /trips endpoint.
        """
        trips = []
        for _ in range(10):
            user = await UserFactory()
            trip = await TripFactory(author_id=user.id)
            trips.append(trip.name)
        response = await ac.get("/trips")
        assert response.status_code == HTTPStatus.OK
        for trip in trips:
            assert any(response_trip["name"] == trip for response_trip in response.json())

    async def test_trip_detail(self, ac: AsyncClient):
        """
        Test trip detail endpoint.

        Create a trip and check if it appears on /trips/{trip_id} endpoint.
        """
        user = await UserFactory()
        trip = await TripFactory(author_id=user.id)
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

    async def test_location_creation(self, ac, authenticated_ac: AsyncClient):
        """
        Test location creation endpoint.

        Create a trip and add a location to it.
        1. Check location creation for an authenticated user.
        2. Check location creation for a user who is not the author of the trip.
        3. Check location creation for an anonymous user.s
        """

        async def test_loc(user_id, status, anonymous=False):
            trip = await TripFactory(author_id=user_id)
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

        await test_loc(authenticated_ac.user.id, HTTPStatus.CREATED)
        user = await UserFactory()
        await test_loc(user.id, HTTPStatus.FORBIDDEN)
        await test_loc(user.id, HTTPStatus.UNAUTHORIZED, anonymous=True)

    async def test_get_locations(self, authenticated_ac: AsyncClient):
        """
        Test get locations endpoint.

        Create a trip, add some locations to it,
         and check if the get locations endpoint returns them.
        """
        user = await UserFactory()
        trip = await TripFactory(author_id=user.id)
        for _ in range(3):
            await LocationFactory(trip_id=trip.id)

        response = await authenticated_ac.get(f"/trips/{trip.id}/locations")
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()) == 3
