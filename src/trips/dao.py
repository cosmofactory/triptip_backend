from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.dao.base import BaseDAO
from src.trips.models import Highlight, Location, Route, Trip


class TripDAO(BaseDAO):
    """Database access object for Trip."""

    model = Trip

    async def get_all_trips(self, limit: int) -> list[Trip]:
        """Get list of trips joined with authors."""
        query = select(Trip).options(joinedload(Trip.author)).limit(limit)
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def get_all_and_count(self, **filter_params):
        """
        Get all objects from the table with total number of objects.

        Returns mapped dict view.
        If filter_params are provided, filter the objects by the given parameters.
        """
        total_count = func.count().over().label("total_count")
        query = select(self.model.__table__.columns, total_count).filter_by(**filter_params)
        result = await self.db.execute(query)
        return result.mappings().all()


class LocationDAO(BaseDAO):
    """Database access object for Location."""

    model = Location


class RouteDAO(BaseDAO):
    """Database access object for Route."""

    model = Route


class HighlightDAO(BaseDAO):
    """Database access object for Highlight."""

    model = Highlight
