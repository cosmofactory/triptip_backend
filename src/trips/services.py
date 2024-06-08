from fastapi import HTTPException, status

from src.trips.dao import LocationDAO, TripDAO
from src.trips.schemas import SDetailedTripOutput, SLocationInput, STripInput, STripOutput


class TripService:
    """Service layer for Trip."""

    @staticmethod
    async def get_trips(limit: int) -> list[STripOutput]:
        """Get list of trips."""
        trips = await TripDAO.get_all(limit)
        return trips

    @staticmethod
    async def get_trip(trip_id: int) -> SDetailedTripOutput:
        """Get detailed trip information."""
        trip = await TripDAO.get_object_or_404(id=trip_id)
        return trip

    @staticmethod
    async def create_trip(trip_data: STripInput, user_id: int) -> STripOutput:
        """Create a new trip."""
        trip_data = trip_data.model_dump()
        trip_data["author_id"] = user_id
        created_trip = await TripDAO.create(**trip_data)
        return created_trip

    @staticmethod
    async def create_location(trip_id: int, location_data: SLocationInput, user_id: int):
        """Create a new location."""
        # TODO это говнокод, надо сделать нормальный класс PermissionService
        trip = await TripDAO.get_object_or_404(id=trip_id)
        if trip.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't add data to the trip of another user",
            )
        location_data = location_data.model_dump()
        location_data["trip_id"] = trip_id
        created_location = await LocationDAO.create(**location_data)
        return created_location

    @staticmethod
    async def get_locations(trip_id: int):
        """Get list of locations for a trip."""
        locations = await LocationDAO.get_all(trip_id=trip_id)
        return locations
