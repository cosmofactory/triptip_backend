from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import TimeStampModel

if TYPE_CHECKING:
    from src.users.models import User


class Subscriptions(TimeStampModel):
    """
    Subscriptions model for tracking user's follows.
    """

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    followee_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
        
    #current user is subscriber
    follower: Mapped["User"] = relationship(
        "User",
        back_populates="followings",
        foreign_keys=[follower_id],
    )
    #the one who is subscribed to current user
    followee: Mapped["User"] = relationship(
        "User",
        back_populates="followers",
        foreign_keys=[followee_id],
    )
    
    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="uq_subscriptions_follower_followee"),
        CheckConstraint("follower_id <> followee_id", name="ck_subscriptions_not_self_follow"),
    )
    