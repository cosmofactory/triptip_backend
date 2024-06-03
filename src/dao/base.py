from fastapi import HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from src.database.database import async_session_maker


class BaseDAO:
    """Abstract class for ORM requests."""

    model = None

    @classmethod
    async def get_all(cls, **filter_params):
        """
        Get all objects from the table.

        Returns mapped dict view.
        If filter_params are provided, filter the objects by the given parameters.
        """
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_params)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def get_object_or_404(cls, **filter_params):
        """
        Get one object from the table.

        If no object found raise 404.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_params)
            result = await session.execute(query)
            if result := result.unique().scalar_one_or_none():
                return result
            else:
                raise HTTPException(status_code=404, detail="Object not found")

    @classmethod
    async def get_one_or_none(cls, **filter_params):
        """
        Get one object from the table.

        If no object found raise 404.
        """
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_params)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def create(cls, **object_data):
        """Create object in the table."""
        async with async_session_maker() as session:
            query = insert(cls.model).values(**object_data).returning(cls.model)
            try:
                result = await session.execute(query)
                await session.commit()
                return result.scalars().first()
            except IntegrityError:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Object already exists"
                ) from None
