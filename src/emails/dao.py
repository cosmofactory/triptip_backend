from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.emails.models import Emails


class EmailDAO(BaseDAO):
    """DAO for Emails limits model"""

    model = Emails

    @classmethod
    async def get_user_daily_email_record(cls, db: AsyncSession, user_id: int):
        """Get user daily email record"""
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        next_day = start_of_day + timedelta(days=1)
        query = select(cls.model).where(
            and_(
                cls.model.user_id == user_id,
                cls.model.created_at >= start_of_day,
                cls.model.created_at < next_day,
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_global_daily_email_record(cls, db: AsyncSession):
        """Get email record including all users"""
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        next_day = start_of_day + timedelta(days=1)
        query = select(func.sum(cls.model.emails_counter)).where(
            and_(cls.model.created_at >= start_of_day, cls.model.created_at < next_day)
        )
        result = await db.execute(query)
        return result.scalar() or 0

    @classmethod
    async def increment_emails_count(cls, db: AsyncSession, user_id: int):
        """Increment user daily email record"""
        start_of_day = datetime.combine(date.today(), datetime.min.time())
        next_day = start_of_day + timedelta(days=1)
        query = (
            update(cls.model)
            .where(
                and_(
                    cls.model.user_id == user_id,
                    cls.model.created_at >= start_of_day,
                    cls.model.created_at < next_day,
                )
            )
            .values(emails_counter=cls.model.emails_counter + 1)
        )
        await db.execute(query)
        await db.commit()
