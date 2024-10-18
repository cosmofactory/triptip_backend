from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.trips.models import Location, Route, Trip


class TripDAO(BaseDAO):
    """Database access object for Trip."""

    model = Trip

    @classmethod
    async def get_all_trips(cls, db: AsyncSession, limit: int) -> dict:
        """Get list of trips."""
        query = select(
            Trip.id,
            Trip.name,
            Trip.description,
            Trip.region,
            Trip.date_from,
            Trip.date_to,
            Trip.author_id,
        ).limit(limit)
        result = await db.execute(query)
        return result.mappings().all()


class LocationDAO(BaseDAO):
    """Database access object for Location."""

    model = Location


class RouteDAO(BaseDAO):
    """Database access object for Route."""

    model = Route
