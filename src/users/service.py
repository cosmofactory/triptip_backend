from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.dao import UserDAO
from src.users.schemas import SUserOutput


class UserService:
    """Service layer for users module."""

    @staticmethod
    async def get_all_users(db: AsyncSession) -> List[SUserOutput]:
        """Return all users from the database."""
        return await UserDAO.get_all(db)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> SUserOutput:
        """Return user by id."""
        return await UserDAO.get_object_or_404(db, id=user_id)
