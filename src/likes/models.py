from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import TimeStampModel

if TYPE_CHECKING:
    from src.trips.models import Trip


class Like(TimeStampModel):
    """
    Likes model for tracking likes under trip records.
    """

    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))

    trip: Mapped["Trip"] = relationship(
        "Trip",
        back_populates="likes",
        foreign_keys="[Like.trip_id]",
        lazy="joined",
    )
