from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.auth import get_current_user
from src.database.database import SessionDep
from src.trips.schemas import STripOutput
from src.users.schemas import SUserNotFound, SUserOutput
from src.users.service import UserService
from src.utils.dependencies import upload_image
from src.utils.exceptions import SErrorResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_all_users(db: SessionDep) -> list[SUserOutput]:
    """Get all users."""
    result = await UserService.get_all_users(db)
    return result


@router.get("/get_user/{user_id}", responses={404: {"model": SUserNotFound}})
async def get_user(user_id: int, db: SessionDep) -> SUserOutput:
    """Get user by id."""
    result = await UserService.get_user_by_id(db, user_id=user_id)
    return result


@router.get(
    "/me",
)
async def read_users_me(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
) -> SUserOutput:
    """Get current user."""
    return current_user


@router.post(
    "/me/userpic_upload",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_400_BAD_REQUEST: {"model": SErrorResponse}},
)
async def userpic_upload(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
    userpic: Annotated[str, Depends(upload_image)],
    db: SessionDep,
) -> SUserOutput:
    user = await UserService.upload_userpic_to_current_user(db, current_user, userpic)
    return user


@router.get("/get_user/{user_id}/trips")
async def get_user_trips(user_id: int, db: SessionDep) -> list[STripOutput]:
    result = await UserService.get_user_trips(db, user_id)
    return result
