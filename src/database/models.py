import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.database.database import Base


class TimeStampModel(Base):
    """
    Abstract model for universal and timestamp columns.

    created_at - timestamp of creation,
    updated_at - timestamp of last update, autoupdates on every update,
    deleted_at - timestamp of deletion, nullable.
    """

    __abstract__ = True

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
