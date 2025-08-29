from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.subscriptions.models import Subscriptions
from src.users.models import User


class SubscriptionDAO(BaseDAO):
    """DAO for Subscriptions limits model"""

    model = Subscriptions

    @classmethod
    async def find_by_user_id(cls, db: AsyncSession, followee_ids: list) -> list[User] | None:
        query = select(User).where(User.id.in_(followee_ids))
        result = await db.execute(query)
        return result.unique().scalars().all() if result else None
