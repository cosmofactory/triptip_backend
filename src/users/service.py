from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.trips.dao import TripDAO
from src.trips.schemas import STripListOutput
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

    @staticmethod
    async def upload_userpic_to_current_user(
        db: AsyncSession, user: SUserOutput, userpic: str
    ) -> SUserOutput:
        user.userpic = userpic
        user = await UserDAO.update(db, user.id, **user.model_dump(include={"userpic"}))
        return SUserOutput.model_validate(user)

    @staticmethod
    async def get_user_trips(db: AsyncSession, user_id: int) -> STripListOutput:
        trips = await TripDAO.get_all_and_count(db, author_id=user_id)
        if trips:
            total_count = trips[0].get("total_count", 0)
            return STripListOutput(trips=trips, total_count=total_count)
        return STripListOutput(trips=trips, total_count=0)
