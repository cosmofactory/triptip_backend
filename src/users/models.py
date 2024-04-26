from pydantic import EmailStr
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models import TimeStampModel


class User(TimeStampModel):
    """User model."""

    __tablename__ = "users"

    email: Mapped[EmailStr] = mapped_column(String(256), unique=True)
    username: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str]
    userpic: Mapped[str | None]
    bio: Mapped[str | None] = mapped_column(Text(1000), nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email})"
