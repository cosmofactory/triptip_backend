from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.emails.models import Emails
from src.settings.config import settings


class EmailDAO(BaseDAO):
    """DAO for Emails limits model"""

    model = Emails

    @classmethod
    async def can_send_email(cls, db: AsyncSession, user_id: int) -> bool:
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
        user_record = result.scalar_one_or_none()
        if user_record and user_record.emails_counter >= settings.USER_DAILY_LIMIT:
            return False

        query = select(func.sum(cls.model.emails_counter)).where(
            and_(cls.model.created_at >= start_of_day, cls.model.created_at < next_day)
        )
        result = await db.execute(query)
        global_record = result.scalar() or 0
        if global_record >= settings.GLOBAL_DAILY_LIMIT:
            return False
        return True

    @classmethod
    async def increment_emails_count(cls, db: AsyncSession, user_id: int):
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
