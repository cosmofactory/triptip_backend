from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import TimeStampModel

if TYPE_CHECKING:
    from src.users.models import User


class Emails(TimeStampModel):
    """
    Emails limiter model for tracking email sending per user and globally.
    """

    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    emails_counter: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship("User")
