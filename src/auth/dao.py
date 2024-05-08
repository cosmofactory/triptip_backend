from sqlalchemy import desc, select

from src.auth.models import RefreshToken
from src.dao.base import BaseDAO
from src.database.database import async_session_maker
from src.users.models import User


class AuthDAO(BaseDAO):
    model = User


class RefreshTokenDAO(BaseDAO):
    model = RefreshToken

    @classmethod
    async def get_last_token(cls, user_id: int, order_by, limit: int) -> dict:
        """Get the last token for the user based on the order_by column."""
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).order_by(desc(order_by)).limit(limit)
            result = await session.execute(query)
            return result.mappings().one_or_none()
