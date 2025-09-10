import logfire
from sqlalchemy.ext.asyncio import AsyncSession

from src.comments.dao import CommentDAO
from src.comments.schemas import SCommentInput


class CommentService:
    "Service layer for Comment."

    @staticmethod
    @logfire.instrument()
    async def create_comment(
        db: AsyncSession,
        trip_id: int,
        author_id: int,
        comment_data: SCommentInput,
    ):
        """Create a new comment."""
        comment_data = comment_data.model_dump()
        comment_data["trip_id"] = trip_id
        comment_data["author_id"] = author_id
        comment_data["text"] = comment_data["text"].strip()
        created_comment = await CommentDAO.create(db, **comment_data)
        return created_comment

    @staticmethod
    @logfire.instrument()
    async def get_comments(db: AsyncSession, trip_id: int):
        """Get list of comments of a trip."""
        comments = await CommentDAO.get_all(db, trip_id=trip_id)
        return comments

    @staticmethod
    @logfire.instrument()
    async def delete_comment(db: AsyncSession, comment_id: int) -> None:
        """Delete an existing comment."""
        await CommentDAO.delete(db, comment_id)
        return None
