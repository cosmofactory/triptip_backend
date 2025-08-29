from typing import List

from fastapi import HTTPException, status

import logfire
from sqlalchemy.ext.asyncio import AsyncSession

from src.trips.dao import TripDAO
from src.trips.schemas import STripListOutput
from src.users.dao import UserDAO
from src.subscriptions.dao import SubscriptionDAO
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

    @staticmethod
    async def get_user_trips(db: AsyncSession, user_id: int) -> STripListOutput:
        trips = await TripDAO.get_all_and_count(db, author_id=user_id)
        if trips:
            total_count = trips[0].get("total_count", 0)
            return STripListOutput(trips=trips, total_count=total_count)
        return STripListOutput(trips=trips, total_count=0)

    @staticmethod
    async def follow_to_current_user(
        db: AsyncSession,
        current_user: SUserOutput,
        followee_id: int,
    ) -> dict:
        """
        Follow to user if not followed. If followed, raise an error.
        
        Make sure that you cannot follow yourself.
        """
        followee = await UserDAO.get_object_or_404(db, id=followee_id)
        if current_user.id == followee.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot follow yourself",
            )
        subscription = await SubscriptionDAO.get_one_or_none(
            db,
            follower_id=current_user.id,
            followee_id=followee.id,
        )
        if subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already following this user",
            )
        new_subscription = await SubscriptionDAO.create(
            db,
            follower_id=current_user.id,
            followee_id=followee.id,
        )
        return {"id": new_subscription.id, "follower_id": current_user.id, "followee_id": followee.id}
    
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
        followee = await UserDAO.get_object_or_404(db, id=followee_id)
        if current_user.id == followee.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot unfollow yourself",
            )
        subscription = await SubscriptionDAO.get_one_or_none(
            db,
            follower_id=current_user.id,
            followee_id=followee.id,
        )
        if subscription is None:
            return None
        await SubscriptionDAO.delete(db, subscription["id"])
        return None
    
    @staticmethod
    async def get_all_followings(
        db: AsyncSession,
        user_id: int,
    ) -> List[SUserOutput]:
        subscriptions = await SubscriptionDAO.get_all(db, follower_id=user_id)
        followee_ids = [row["followee_id"] for row in subscriptions]
        if not followee_ids:
            return []
        users = await SubscriptionDAO.find_by_user_id(db, followee_ids)
        return [SUserOutput.model_validate(user) for user in users]