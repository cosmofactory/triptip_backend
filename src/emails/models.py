from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import TimeStampModel

if TYPE_CHECKING:
    from src.users.models import User


class Emails(TimeStampModel):
    """
    Email limiter model for tracking email sending per user and globally.
    - Per user: 20 emails per day
    - Global: 2000 emails per day
    """

    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    emails_counter: Mapped[int] = mapped_column(Integer, default=0)

    author: Mapped["User"] = relationship("User", back_populates="emails")
