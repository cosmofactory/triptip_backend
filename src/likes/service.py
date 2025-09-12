import logfire
from sqlalchemy.ext.asyncio import AsyncSession

from src.likes.dao import LikeDAO


class LikeService:
    "Service layer for Like."

    @staticmethod
    @logfire.instrument()
    async def leave_like(
        db: AsyncSession,
        trip_id: int,
        author_id: int,
    ):
        """Leave a like."""
        like_data = dict()
        like_data["trip_id"] = trip_id
        like_data["author_id"] = author_id
        posted_like = await LikeDAO.create(db, **like_data)
        return posted_like

    @staticmethod
    @logfire.instrument()
    async def discard_like(
        db: AsyncSession,
        user_id: int,
        trip_id: int,
    ) -> None:
        """Unlike current trip."""
        like = await LikeDAO.get_one_or_none(
            db,
            author_id=user_id,
            trip_id=trip_id,
        )
        if like is None:
            return None
        await LikeDAO.delete(db, like.id)
        return None
