from typing import TYPE_CHECKING, List

from pydantic import EmailStr
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import TimeStampModel

if TYPE_CHECKING:
    from src.auth.models import RefreshToken
    from src.trips.models import Route, Trip


class User(TimeStampModel):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[EmailStr] = mapped_column(String(256), unique=True)
    username: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str]
    userpic: Mapped[str | None]
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    trips: Mapped[List["Trip"]] = relationship(
        "Trip",
        back_populates="author",
        lazy="joined",
        cascade="save-update, merge",
    )
    routes: Mapped[List["Route"]] = relationship(
        "Route",
        back_populates="author",
        lazy="joined",
        cascade="save-update, merge",
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        cascade="all, delete",
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email})"
