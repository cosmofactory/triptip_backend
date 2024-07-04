from typing import Type

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.users.models import User


class Permissions:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_author_or_read_only(
        self, obj_id: int, dao_class: Type[BaseDAO], user: User
    ) -> None:
        obj = await dao_class.get_object_or_404(self.db, id=obj_id)
        if obj.author_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action.",
            )
