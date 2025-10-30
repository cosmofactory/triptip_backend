from typing import List, Literal

import logfire
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.likes.dao import LikeDAO
from src.subscriptions.dao import SubscriptionDAO
from src.trips.dao import TripDAO
from src.trips.schemas import STripListOutput
from src.users.dao import UserDAO
from src.users.schemas import SUserOutput


class UserService:
    """Service layer for users module."""

    @logfire.instrument()
    @staticmethod
    async def get_all_users(db: AsyncSession) -> List[SUserOutput]:
        """Return all users from the database."""
        return await UserDAO.get_all(db)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> SUserOutput:
        """Return user by id."""
        return await UserDAO.get_object_or_404(db, id=user_id)

    @staticmethod
    async def upload_userpic_to_current_user(
        db: AsyncSession, user: SUserOutput, userpic: str
    ) -> SUserOutput:
        user.userpic = userpic
        user = await UserDAO.update(db, user.id, **user.model_dump(include={"userpic"}))
        return SUserOutput.model_validate(user)

    @logfire.instrument()
    @staticmethod
    async def delete_account(db: AsyncSession, user_id: int) -> None:
        """Soft deletion of a user account."""
        await UserDAO.delete(db, user_id, soft_delete=True)
        return None

    @staticmethod
    async def get_user_trips(db: AsyncSession, user_id: int) -> STripListOutput:
        trips = await TripDAO.get_all_and_count(db, author_id=user_id)
        if trips:
            total_count = trips[0].get("total_count", 0)
            return STripListOutput(trips=trips, total_count=total_count)
        return STripListOutput(trips=trips, total_count=0)

    @staticmethod
    async def follow_current_user(
        db: AsyncSession,
        current_user: SUserOutput,
        followee_id: int,
    ) -> dict:
        """
        Follow user if not followed. If followed, raise an error.

        Make sure that you cannot follow yourself.
        """
        if current_user.id == followee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot follow yourself",
            )
        try:
            subscription = await SubscriptionDAO.create(
                db,
                follower_id=current_user.id,
                followee_id=followee_id,
            )
            await UserDAO.increment_counter(db, current_user.id, "followings_counter")
        except HTTPException as e:
            if e.status_code == status.HTTP_400_BAD_REQUEST:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User does not exist or already followed",
                ) from e
            raise
        return {
            "id": subscription.id,
            "follower_id": current_user.id,
            "followee_id": followee_id,
        }

    @staticmethod
    async def unfollow_current_user(
        db: AsyncSession,
        current_user: SUserOutput,
        followee_id: int,
    ) -> None:
        """
        Unfollow user.

        Make sure that you cannot unfollow yourself.
        """
        if current_user.id == followee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot unfollow yourself",
            )

        subscription = await SubscriptionDAO.get_one_or_none(
            db,
            follower_id=current_user.id,
            followee_id=followee_id,
        )
        if subscription is None:
            return None
        await SubscriptionDAO.delete(db, subscription.id)
        await UserDAO.decrement_counter(db, current_user.id, "followings_counter")
        return None

    @staticmethod
    async def get_all_related_users(
        db: AsyncSession, type_id: int, relation_type: Literal["subscription", "like"]
    ) -> List[SUserOutput]:
        """
        Get all users based on the relation type.
        """
        match relation_type:
            case "subscription":
                subscriptions = await SubscriptionDAO.get_all(db, follower_id=type_id)
                if not subscriptions:
                    return []

                related_ids = [row.followee_id for row in subscriptions]
                if not related_ids:
                    return []
            case "like":
                likes = await LikeDAO.get_all(db, trip_id=type_id)
                if not likes:
                    return []

                related_ids = [row.author_id for row in likes]
                if not related_ids:
                    return []
            case _:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid relation_type for getting all related",
                )

        users = await UserDAO.find_by_ids(db, related_ids)
        return [SUserOutput.model_validate(user) for user in users]

    @staticmethod
    async def get_related_quantity(
        db: AsyncSession, type_id: int, relation_type: Literal["subscription", "like"]
    ) -> int:
        """
        Get quantity of users based on the relation type.
        """
        match relation_type:
            case "subscription":
                related_quantity = await SubscriptionDAO.count_by_filter(
                    db,
                    follower_id=type_id,
                )
            case "like":
                related_quantity = await LikeDAO.count_by_filter(
                    db,
                    trip_id=type_id,
                )
            case _:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid relation_type for getting related quantity",
                )
        return related_quantity
