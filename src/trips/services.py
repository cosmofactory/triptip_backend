from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.trips.dao import LocationDAO, TripDAO
from src.trips.schemas import SDetailedTripOutput, SLocationInput, STripInput, STripOutput


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
        # TODO это говнокод, надо сделать нормальный класс PermissionService
        trip = await TripDAO.get_object_or_404(db, id=trip_id)
        if trip.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't add data to the trip of another user",
            )
        location_data = location_data.model_dump()
        location_data["trip_id"] = trip_id
        created_location = await LocationDAO.create(db, **location_data)
        return created_location

    @staticmethod
    async def get_locations(db: AsyncSession, trip_id: int):
        """Get list of locations for a trip."""
        locations = await LocationDAO.get_all(db, trip_id=trip_id)
        return locations
