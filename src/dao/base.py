import logfire
from fastapi import HTTPException, status
from sqlalchemy import case, delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    """Abstract class for ORM requests."""

    model = None

    @classmethod
    @logfire.instrument()
    async def get_all(
        cls,
        db: AsyncSession,
        limit: int | None = None,
        include_deleted: bool = False,
        **filter_params,
    ):
        """
        Get all objects from the table.

        Returns mapped dict view.
        If filter_params are provided, filter the objects by the given parameters.

        param: include_deleted determines what objects will be returned:
        all (existing and soft deleted) or only existing objects.
        """
        if not include_deleted:
            filter_params["deleted"] = False
        query = select(cls.model.__table__.columns).filter_by(**filter_params).limit(limit)
        result = await db.execute(query)
        return result.mappings().all()

    @classmethod
    async def get_object_or_404(
        cls,
        db: AsyncSession,
        include_deleted: bool = False,
        **filter_params,
    ):
        """
        Get one object from the table.

        If no object found raise 404.

        param: include_deleted determines whether or not soft-deleted object will be returned.
        """
        if not include_deleted:
            filter_params["deleted"] = False
        query = select(cls.model).filter_by(**filter_params)
        result = await db.execute(query)
        if result := result.unique().scalar_one_or_none():
            return result
        else:
            raise HTTPException(status_code=404, detail="Object not found")

    @classmethod
    async def get_one_or_none(
        cls,
        db: AsyncSession,
        include_deleted: bool = False,
        **filter_params: dict,
    ):
        """
        Get one object from the table.

        If no object is found, return None.

        param: include_deleted determines whether or not soft-deleted object will be returned.
        """
        if not include_deleted:
            filter_params["deleted"] = False
        query = select(cls.model.__table__.columns).filter_by(**filter_params)
        result = await db.execute(query)
        return result.mappings().one_or_none()

    @classmethod
    async def count_by_filter(
        cls,
        db: AsyncSession,
        include_deleted: bool = False,
        **filter_params,
    ):
        """
        Count objects in the table by specific filter parameters.

        If no objects match the filter, returns 0.

        param: include_deleted determines whether or not soft-deleted object will be returned.
        """
        if not include_deleted:
            filter_params["deleted"] = False
        query = select(func.count(cls.model.id)).select_from(cls.model).filter_by(**filter_params)
        result = await db.execute(query)
        return result.scalar() or 0

    @classmethod
    async def increment_counter(cls, db: AsyncSession, obj_id: int, field: str):
        """Increment any counter field."""
        query = (
            update(cls.model)
            .where(cls.model.id == obj_id)
            .values({field: getattr(cls.model, field) + 1})
        )
        await db.execute(query)
        await db.commit()

    @classmethod
    async def decrement_counter(cls, db: AsyncSession, obj_id: int, field: str):
        """Decrement any counter field, not below zero."""
        column = getattr(cls.model, field)
        query = (
            update(cls.model)
            .where(cls.model.id == obj_id)
            .values({field: case((column > 0, column - 1), else_=0)})
        )
        await db.execute(query)
        await db.commit()

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

    @classmethod
    async def delete(
        cls,
        db: AsyncSession,
        obj_id: int,
        soft_delete: bool = True,
    ) -> None:
        """
        Soft or hard delete object by its id.
        param: soft_delete determines whether to soft or hard delete the object.

        If there is no object -> Status_Code = 404.

        If soft_delete is True, soft delete the object:
            1. set param: deleted = True.
            2. object remains in database.
        Else delete the object from table.
        """
        if soft_delete:
            obj = await cls.get_object_or_404(db, id=obj_id)
            query = update(cls.model).where(cls.model.id == obj.id).values(deleted=True)
        else:
            obj = await cls.get_object_or_404(db, id=obj_id)
            query = delete(cls.model).where(cls.model.id == obj.id)
        await db.execute(query)
        await db.commit()

    @classmethod
    async def restore(cls, db: AsyncSession, obj_id: int):
        """
        Restore object after soft deletion.

        If object exists -> restore it.
        Else Status_Code = 404.
        """
        obj = await cls.get_object_or_404(db, id=obj_id, deleted=True)

        query = update(cls.model).where(cls.model.id == obj.id).values(deleted=False)
        await db.execute(query)
        await db.commit()
