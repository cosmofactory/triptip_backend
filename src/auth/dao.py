from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import RefreshToken
from src.dao.base import BaseDAO
from src.users.models import User


class AuthDAO(BaseDAO):
    model = User


class RefreshTokenDAO(BaseDAO):
    model = RefreshToken

    async def get_last_token(self, user_id: int, order_by, limit: int) -> dict:
        """Get the last token for the user based on the order_by column."""
        query = select(self.model.__table__.columns).order_by(desc(order_by)).limit(limit)
        result = await self.db.execute(query)
        return result.mappings().one_or_none()
