import logfire
from fastapi import HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    """Abstract class for ORM requests."""

    model = None

    def __init__(self, db: AsyncSession):
        self.db = db

    @logfire.instrument()
    async def get_all(self, limit: int | None = None, **filter_params):
        """
        Get all objects from the table.

        Returns mapped dict view.
        If filter_params are provided, filter the objects by the given parameters.
        """
        query = select(self.model.__table__.columns).filter_by(**filter_params).limit(limit)
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_object_or_404(self, **filter_params):
        """
        Get one object from the table.

        If no object found raise 404.
        """
        query = select(self.model).filter_by(**filter_params)
        result = await self.db.execute(query)
        if result := result.unique().scalar_one_or_none():
            return result
        else:
            raise HTTPException(status_code=404, detail="Object not found")

    async def get_one_or_none(self, **filter_params: dict):
        """
        Get one object from the table.

        If no object is found, return None.
        """
        query = select(self.model.__table__.columns).filter_by(**filter_params)
        result = await self.db.execute(query)
        return result.mappings().one_or_none()

    async def create(self, **object_data: dict):
        """Create object in the table."""
        query = insert(self.model).values(**object_data).returning(self.model)
        try:
            result = await self.db.execute(query)
            await self.db.commit()
            return result.scalars().first()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Object already exists"
            ) from None

    async def update(self, obj_id: int, **object_data: dict):
        """Update object in the table."""
        query = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**object_data)
            .returning(self.model)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalars().first()

    async def delete(self, obj_id: int) -> None:
        """Delete object in the table.

        Query to db (by obj_id)
        If there is no object -> Status_Code = 404
        Else delete it
        """
        query = delete(self.model).where(self.model.id == obj_id)
        result = await self.db.execute(query)
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {self.model.__name__} found with id {obj_id}",
            )
        await self.db.commit()
