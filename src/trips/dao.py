from sqlalchemy import select

from src.dao.base import BaseDAO
from src.database.database import async_session_maker
from src.trips.models import Location, Trip


class TripDAO(BaseDAO):
    """Database access object for Trip."""

    model = Trip

    @classmethod
    async def get_all(cls, limit: int) -> dict:
        """Get list of trips."""
        async with async_session_maker() as session:
            query = select(
                Trip.id, Trip.name, Trip.description, Trip.date_from, Trip.date_to, Trip.author_id
            ).limit(limit)
            result = await session.execute(query)
            return result.mappings().all()


class LocationDAO(BaseDAO):
    """Database access object for Location."""

    model = Location
