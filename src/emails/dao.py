from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.base import BaseDAO
from src.emails.models import Emails


class EmailDAO(BaseDAO):
    """DAO for Emails limits model"""

    model = Emails

    async def get_user_daily_email_record(self, user_id: int):
        """Get user daily email record"""
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        next_day = start_of_day + timedelta(days=1)
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.created_at >= start_of_day,
                self.model.created_at < next_day,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_global_daily_email_record(self):
        """Get email record including all users"""
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        next_day = start_of_day + timedelta(days=1)
        query = select(func.sum(self.model.emails_counter)).where(
            and_(self.model.created_at >= start_of_day, self.model.created_at < next_day)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def increment_emails_count(self, user_id: int):
        """Increment user daily email record"""
        start_of_day = datetime.combine(date.today(), datetime.min.time())
        next_day = start_of_day + timedelta(days=1)
        query = (
            update(self.model)
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.created_at >= start_of_day,
                    self.model.created_at < next_day,
                )
            )
            .values(emails_counter=self.model.emails_counter + 1)
        )
        await self.db.execute(query)
        await self.db.commit()
