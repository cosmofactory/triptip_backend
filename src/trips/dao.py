from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.dao.base import BaseDAO
from src.trips.models import Highlight, Location, Route, Trip


class TripDAO(BaseDAO):
    """Database access object for Trip."""

    model = Trip

    @classmethod
    async def get_all_trips(cls, db: AsyncSession, params):
        """
        Get list of trips with nested author fields for pagination:
            1. Get SQLAlchemy query for trips with nested author fields
            2. Use apaginate to paginate the query
            3. Return the result.
        """
        query = select(Trip).options(joinedload(Trip.author))
        return await apaginate(db, query, params)

    @classmethod
    async def get_all_and_count(cls, db: AsyncSession, **filter_params):
        """
        Get all objects from the table with total number of objects.

        Returns mapped dict view.
        If filter_params are provided, filter the objects by the given parameters.
        """
        total_count = func.count().over().label("total_count")
        query = select(cls.model.__table__.columns, total_count).filter_by(**filter_params)
        result = await db.execute(query)
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
