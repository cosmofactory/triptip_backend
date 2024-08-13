from sqlalchemy.ext.asyncio import AsyncSession

from src.trips.dao import LocationDAO, RouteDAO, TripDAO
from src.trips.schemas import (
    SDetailedTripOutput,
    SLocationInput,
    SRouteInput,
    STripInput,
    STripOutput,
)


class TripService:
    """Service layer for Trip."""

    @staticmethod
    async def get_trips(db: AsyncSession, limit: int) -> list[STripOutput]:
        """Get list of trips."""
        trips = await TripDAO.get_all(db, limit)
        return trips

    @staticmethod
    async def get_trip(db: AsyncSession, trip_id: int) -> SDetailedTripOutput:
        """Get detailed trip information."""
        trip = await TripDAO.get_object_or_404(db, id=trip_id)
        return trip

    @staticmethod
    async def create_trip(db: AsyncSession, trip_data: STripInput, user_id: int) -> STripOutput:
        """Create a new trip."""
        trip_data = trip_data.model_dump()
        trip_data["author_id"] = user_id
        created_trip = await TripDAO.create(db, **trip_data)
        return created_trip

    @staticmethod
    async def create_location(
        db: AsyncSession, trip_id: int, location_data: SLocationInput, user_id: int
    ):
        """Create a new location."""
        location_data = location_data.model_dump()
        location_data["trip_id"] = trip_id
        created_location = await LocationDAO.create(db, **location_data)
        return created_location

    @staticmethod
    async def get_locations(db: AsyncSession, trip_id: int):
        """Get list of locations for a trip."""
        locations = await LocationDAO.get_all(db, trip_id=trip_id)
        return locations

    @staticmethod
    async def get_route(db: AsyncSession, location_id: int):
        """Get route between two locations."""
        route = await RouteDAO.get_object_or_404(db, origin_id=location_id)
        return route

    @staticmethod
    async def create_route(db: AsyncSession, route_data: SRouteInput, user_id: int):
        """Create a new route."""
        route_data = route_data.model_dump()
        route_data["author_id"] = user_id
        created_route = await RouteDAO.create(db, **route_data)
        return created_route
