from fastapi import HTTPException, status
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    """Abstract class for ORM requests."""

    model = None

    @classmethod
    async def get_all(cls, db: AsyncSession, limit: int | None = None, **filter_params):
        """
        Get all objects from the table.

        Returns mapped dict view.
        If filter_params are provided, filter the objects by the given parameters.
        """
        query = select(cls.model.__table__.columns).filter_by(**filter_params).limit(limit)
        result = await db.execute(query)
        return result.mappings().all()

    @classmethod
    async def get_object_or_404(cls, db: AsyncSession, **filter_params):
        """
        Get one object from the table.

        If no object found raise 404.
        """
        query = select(cls.model).filter_by(**filter_params)
        result = await db.execute(query)
        if result := result.unique().scalar_one_or_none():
            return result
        else:
            raise HTTPException(status_code=404, detail="Object not found")

    @classmethod
    async def get_one_or_none(cls, db: AsyncSession, **filter_params: dict):
        """
        Get one object from the table.

        If no object is found, return None.
        """
        query = select(cls.model.__table__.columns).filter_by(**filter_params)
        result = await db.execute(query)
        return result.mappings().one_or_none()

    @classmethod
    async def create(cls, db: AsyncSession, **object_data: dict):
        """Create object in the table."""
        query = insert(cls.model).values(**object_data).returning(cls.model)
        try:
            result = await db.execute(query)
            await db.commit()
            return result.scalars().first()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Object already exists"
            ) from None

    @classmethod
    async def update(cls, db: AsyncSession, obj_id: int, **object_data: dict):
        """Update object in the table."""
        query = (
            update(cls.model)
            .where(cls.model.id == obj_id)
            .values(**object_data)
            .returning(cls.model)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalars().first()
