from typing import TYPE_CHECKING, List

from pydantic import EmailStr
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import TimeStampModel

if TYPE_CHECKING:
    from src.trips.models import Trip


class User(TimeStampModel):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[EmailStr] = mapped_column(String(256), unique=True)
    username: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str]
    userpic: Mapped[str | None]
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    trips: Mapped[List["Trip"]] = relationship("Trip", back_populates="author", lazy="selectin")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email})"
