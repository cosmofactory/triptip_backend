from http import HTTPStatus

import pytest
from httpx import AsyncClient
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.trips.dao import LocationDAO, RouteDAO, TripDAO
from src.trips.schemas import SDetailedTripOutput
from tests.factories.trips_factories import (
    HighlightFactory,
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

    async def test_trip_endpoint_delete(
        self,
        authenticated_ac: AsyncClient,
        session: AsyncSession,
        create_trip: TripFactory,
    ):
        """
        Test trip delete endpoint.
        """
        response = await authenticated_ac.delete(f"/trips/{create_trip.id}")
        assert response.status_code == HTTPStatus.NO_CONTENT
        trip = await TripDAO.get_one_or_none(session, id=create_trip.id)
        assert trip is None

    async def test_trip_delete_non_existent(self, authenticated_ac: AsyncClient):
        """
        Test trip deletion endpoint for non-existent trip.

        Check if it returns a 404 error for a non-existent trip ID.
        """
        non_existent_trip_id = 999999
        response = await authenticated_ac.delete(f"/trips/{non_existent_trip_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND

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
        Verify nested author fields.
        """
        trips = []
        for _ in range(10):
            trip = create_trip
            trips.append(trip.name)
        response = await ac.get("/trips")
        assert response.status_code == HTTPStatus.OK
        for trip in trips:
            assert any(response_trip["name"] == trip for response_trip in response.json())
        for trip in response.json():
            assert trip["author"]["id"] is not None
            assert isinstance(trip["author"]["id"], int)

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

    async def test_location_endpoint_delete(
        self,
        authenticated_ac: AsyncClient,
        session: AsyncSession,
        create_location: LocationFactory,
    ):
        """
        Test location endpoint delete.
        """
        response = await authenticated_ac.delete(f"/trips/locations/{create_location.id}")
        assert response.status_code == HTTPStatus.NO_CONTENT
        location = await LocationDAO.get_one_or_none(session, id=create_location.id)
        assert location is None

    async def test_location_endpoint_delete_non_existent(self, authenticated_ac: AsyncClient):
        """
        Test location deletion endpoint for non-existent location.

        Check if it returns a 404 error for a non-existent location ID.
        """
        non_existent_id = 999999
        response = await authenticated_ac.delete(f"/trips/locations/{non_existent_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND

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

    async def test_route_endpoint_get(
        self, authenticated_ac: AsyncClient, create_route: RouteFactory
    ):
        """
        Test route endpoint.
        """
        route = create_route

        response = await authenticated_ac.get(f"/trips/locations/{route.origin_id}/route")
        assert response.status_code == HTTPStatus.OK
        assert response.json()["origin_id"] == route.origin_id
        assert response.json()["destination_id"] == route.destination_id

    async def test_route_endpoint_delete(
        self, authenticated_ac: AsyncClient, session: AsyncSession, create_route: RouteFactory
    ):
        """
        Test route deletion endpoint.

        Create a route and check if it can be deleted.
        """
        response = await authenticated_ac.delete(f"/trips/route/{create_route.id}")
        assert response.status_code == HTTPStatus.NO_CONTENT
        route = await RouteDAO.get_one_or_none(session, id=create_route.id)
        assert route is None

    async def test_route_endpoint_delete_non_existent(self, authenticated_ac: AsyncClient):
        """
        Test route deletion endpoint for non-existent route.

        Check if it returns a 404 error for a non-existent route ID.
        """
        non_existent_id = 999999
        response = await authenticated_ac.delete(f"/trips/route/{non_existent_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND


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
    authenticated_ac_2: AsyncClient,
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

    async def create_route(auth_client: AsyncClient):
        if anonymous:
            response = await ac.post(f"/trips/locations/{location}/route", json=data)
        else:
            response = await auth_client.post(f"/trips/locations/{location}/route", json=data)
        return response

    if user_id == "authenticated_user":
        response = await create_route(authenticated_ac)
    else:
        response = await create_route(authenticated_ac_2)

    assert response.status_code == expected_status
    if expected_status == HTTPStatus.CREATED:
        assert response.json()["description"] == data["description"]


async def test_route_creation_no_destination(
    authenticated_ac: AsyncClient,
    post_route_data_no_destination: tuple[dict, int],
):
    """
    Test route creation endpoint without destination.
    """
    data, location = post_route_data_no_destination

    async def create_route(auth_client: AsyncClient):
        response = await authenticated_ac.post(f"/trips/locations/{location}/route", json=data)
        return response

    response = await create_route(authenticated_ac)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["description"] == data["description"]


@pytest.mark.parametrize(
    "number_of_trips",
    [
        1,
        10,
        0,
    ],
)
async def test_user_trip_agregation(
    authenticated_ac: AsyncClient,
    session: AsyncSession,
    create_trip_from_second_user,
    number_of_trips,
):
    """
    Test user trip aggregation endpoint.

    1. Create a number of trips for the one user.
    2. Create a trip for a different user.
    3. Check if the endpoint returns only the first user's trips.
    """
    users_trips = []
    user = await UserFactory.create(db=session)
    for _ in range(number_of_trips):
        trip = await TripFactory.create(db=session, author_id=user.id)
        users_trips.append(trip)
    response = await authenticated_ac.get(f"/users/{user.id}/trips")
    assert response.status_code == HTTPStatus.OK
    result = response.json()
    assert result["total_count"] == number_of_trips
    assert len(result["trips"]) == number_of_trips
    for trip in users_trips:
        assert any(response_trip["name"] == trip.name for response_trip in result["trips"])


class TestHighlights:
    async def test_get_route_highlights(
        self, authenticated_ac: AsyncClient, session: AsyncSession, create_route: RouteFactory
    ):
        """
        Test get highlights for route endpoint.

        Create a route, add some highlights to it,
        and check if the get highlights for route endpoint returns them.
        """
        route = create_route
        for _ in range(3):
            await HighlightFactory.create(db=session, route_id=route.id)
        response = await authenticated_ac.get(f"/trips/route/{route.id}/highlights")
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()) == 3

    async def test_get_location_highlights(
        self, authenticated_ac: AsyncClient, session: AsyncSession, create_location: LocationFactory
    ):
        """
        Test get highlights for location endpoint.

        Create a location, add some highlights to it,
        and check if the get highlights for location endpoint returns them.
        """
        location = create_location
        for _ in range(3):
            await HighlightFactory.create(db=session, location_id=location.id)
        response = await authenticated_ac.get(f"/trips/location/{location.id}/highlights")
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()) == 3

    async def test_get_highlight(
        self,
        authenticated_ac: AsyncClient,
        session: AsyncSession,
        create_location_highlight: HighlightFactory,
    ):
        """
        Test get highlight endpoint.

        Create a highlight and check if the get highlight endpoint returns it.
        """
        highlight, location = create_location_highlight
        response = await authenticated_ac.get(f"/trips/highlight/{highlight.id}")
        assert response.status_code == HTTPStatus.OK
        assert response.json()["location_id"] == location.id
