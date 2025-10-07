from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.users.models import User


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def find_by_ids(cls, db: AsyncSession, ids: list[int]) -> list[User]:
        query = select(User).where(User.id.in_(ids))
        result = await db.execute(query)
        return result.unique().scalars().all()
