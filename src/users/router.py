from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.auth import get_current_user
from src.database.database import SessionDep
from src.users.schemas import SUserNotFound, SUserOutput
from src.users.service import UserService

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
