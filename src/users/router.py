from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.auth import get_current_user
from src.users.dao import UserDAO
from src.users.schemas import SUserNotFound, SUserOutput

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_all_users() -> list[SUserOutput]:
    """Get all users."""
    result = await UserDAO.get_all()
    return result


@router.get("/get_user/{user_id}", responses={404: {"model": SUserNotFound}})
async def get_user(user_id: int) -> SUserOutput:
    """Get user by id."""
    result = await UserDAO.get_object_or_404(id=user_id)
    return result


@router.get(
    "/me",
)
async def read_users_me(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
) -> SUserOutput:
    """Get current user."""
    return current_user
