from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.auth import get_current_user
from src.database.database import SessionDep
from src.subscriptions.schemas import SubscriptionOutput
from src.trips.schemas import STripListOutput
from src.users.schemas import SUserNotFound, SUserOutput, SUserSubscriptionOutput
from src.users.service import UserService
from src.utils.dependencies import upload_image
from src.utils.exceptions import SErrorResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_all_users(db: SessionDep) -> list[SUserOutput]:
    """Get all users."""
    result = await UserService.get_all_users(db)
    return result


@router.get("/{user_id}", responses={404: {"model": SUserNotFound}})
async def get_user(user_id: int, db: SessionDep) -> SUserOutput:
    """Get user by id."""
    result = await UserService.get_user_by_id(db, user_id=user_id)
    return result


@router.get(
    "/profile/{user_id}",
)
async def read_users_me(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
    user_id: int,
    db: SessionDep,
) -> SUserOutput:
    """
    Access user profile.

    If it's your own profile, you will see own data with more rights.
    Otherwise you will see just users data.
    """
    if user_id == current_user.id:
        return current_user
    return await UserService.get_user_by_id(db, user_id=user_id)


@router.post(
    "/profile/me/userpic",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SErrorResponse},
    },
)
async def userpic_upload(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
    userpic: Annotated[str, Depends(upload_image)],
    db: SessionDep,
) -> SUserOutput:
    """Upload userpic to current user."""
    user = await UserService.upload_userpic_to_current_user(db, current_user, userpic)
    return user


@router.patch(
    "/profile/me/userpic",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": SErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"description": "User is not authorized"},
    },
)
async def userpic_update(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
    userpic: Annotated[str, Depends(upload_image)],
    db: SessionDep,
) -> SUserOutput:
    """Update userpic to current user."""
    user = await UserService.upload_userpic_to_current_user(db, current_user, userpic)
    return user


@router.delete(
    "/profile/me/delete_account",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User is not authorized"},
    },
)
async def delete_account(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> None:
    """
    Delete user account.

    Soft deletion is implemented for user account.
    """
    await UserService.delete_accont(db, current_user.id)
    return None


@router.get("/{user_id}/trips")
async def get_user_trips(user_id: int, db: SessionDep) -> STripListOutput:
    return await UserService.get_user_trips(db, user_id)


@router.post(
    "/profile/{user_id}/follow",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=SubscriptionOutput,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Can't follow yourself or already following this user"
        },
    },
)
async def follow_user(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
    user_id: int,
    db: SessionDep,
) -> SubscriptionOutput:
    """Follow user."""
    subs_info = await UserService.follow_current_user(db, current_user, user_id)
    return SubscriptionOutput(**subs_info)


@router.delete(
    "/profile/{user_id}/follow",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Can't unfollow yourself"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def unfollow_user(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
    user_id: int,
    db: SessionDep,
) -> None:
    """Unfollow user."""
    await UserService.unfollow_current_user(db, current_user, user_id)
    return None


@router.get(
    "/profile/{user_id}/followings",
    status_code=status.HTTP_200_OK,
    response_model=SUserSubscriptionOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def get_user_followings(user_id: int, db: SessionDep) -> SUserSubscriptionOutput:
    """Get all user's followings."""
    users = await UserService.get_all_related_users(
        db=db,
        type_id=user_id,
        relation_type="subscription",
    )
    followings_counter = await UserService.get_related_quantity(
        db=db,
        type_id=user_id,
        relation_type="subscription",
    )
    return SUserSubscriptionOutput(
        id=user_id,
        followings_counter=followings_counter,
        users=users,
    )
