from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import TimeStampModel

if TYPE_CHECKING:
    from src.users.models import User


class Trip(TimeStampModel):
    """
    Trip model.

    Fetches location data automatically.
    """

    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]]
    date_from: Mapped[date]
    date_to: Mapped[date]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship("User", back_populates="trips")
    locations: Mapped[List["Location"]] = relationship(
        "Location",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"Trip(id={self.id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"Trip(id={self.id}, name={self.name})"


class Location(TimeStampModel):
    """
    Location model.

    name - unique for each trip.
    """

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))

    trip: Mapped["Trip"] = relationship("Trip", back_populates="locations")

    __table_args__ = (UniqueConstraint("trip_id", "name", name="_trip_name_uc"),)

    def __repr__(self) -> str:
        return f"Location(id={self.id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"Location(id={self.id}, name={self.name})"
