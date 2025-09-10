from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import TimeStampModel
from src.settings.enums import RegionEnum

if TYPE_CHECKING:
    from src.comments.models import Comment
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
    region: Mapped[RegionEnum] = mapped_column(Enum(RegionEnum), nullable=False)
    date_from: Mapped[date]
    date_to: Mapped[date]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship("User", back_populates="trips", lazy="selectin")
    locations: Mapped[List["Location"]] = relationship(
        "Location",
        back_populates="trip",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="trip",
        foreign_keys="[Comment.trip_id]",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"Trip(id={self.id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"Trip(id={self.id}, name={self.name})"


class Location(TimeStampModel):
    """
    Location model.

    name - unique for each trip.
    outbound_route - route from this location to another.
    inbound_route - route from another location to this one
    """

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))

    trip: Mapped["Trip"] = relationship("Trip", back_populates="locations", lazy="joined")
    outbound_route: Mapped["Route"] = relationship(
        "Route", back_populates="origin", foreign_keys="[Route.origin_id]"
    )
    inbound_route: Mapped["Route"] = relationship(
        "Route", back_populates="destination", foreign_keys="[Route.destination_id]"
    )
    highlights: Mapped["Highlight"] = relationship("Highlight", back_populates="location")
    sequence_id: Mapped[int]

    __table_args__ = (
        UniqueConstraint("trip_id", "name", name="_trip_name_uc"),
        UniqueConstraint("trip_id", "sequence_id", name="_trip_sequence_uc"),
    )

    @property
    def author_id(self) -> int:
        """Get author_id of the location."""
        return self.trip.author_id

    def __repr__(self) -> str:
        return f"Location(id={self.id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"Location(id={self.id}, name={self.name})"


class Route(TimeStampModel):
    """
    Route model.

    origin_id - location id where route begins
    destination_id - location id where route ends.
    """

    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[Optional[str]]
    origin_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"))
    destination_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"), nullable=True
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship("User", back_populates="routes")
    origin: Mapped["Location"] = relationship(
        "Location",
        back_populates="outbound_route",
        foreign_keys="[Route.origin_id]",
    )
    destination: Mapped["Location"] = relationship(
        "Location",
        back_populates="inbound_route",
        foreign_keys="[Route.destination_id]",
    )
    highlights: Mapped["Highlight"] = relationship("Highlight", back_populates="route")

    def __repr__(self) -> str:
        return f"Route(id={self.id!r}, name={self.description!r})"

    def __str__(self) -> str:
        return f"Route(id={self.id}, name={self.description})"


class Highlight(TimeStampModel):
    """
    Highlight model.
    """

    __tablename__ = "highlights"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]
    route_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"), nullable=True
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"), nullable=True
    )

    route: Mapped["Route"] = relationship("Route", back_populates="highlights", lazy="joined")
    location: Mapped["Location"] = relationship(
        "Location", back_populates="highlights", lazy="joined"
    )

    __table_args__ = (
        CheckConstraint(
            "(route_id IS NOT NULL AND location_id IS NULL) OR (route_id IS NULL AND location_id IS NOT NULL)",
            name="only_one_parent",
        ),
    )

    def __repr__(self) -> str:
        return f"Highlights(id={self.id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"Highlights(id={self.id}, name={self.name})"
