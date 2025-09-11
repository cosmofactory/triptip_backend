from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import TimeStampModel

if TYPE_CHECKING:
    from src.trips.models import Trip


class Comment(TimeStampModel):
    """Comment model"""

    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))
    text: Mapped[str] = mapped_column(Text, nullable=False)

    trip: Mapped["Trip"] = relationship(
        "Trip",
        back_populates="comments",
        foreign_keys="[Comment.trip_id]",
        lazy="joined",
    )
