from fastapi import APIRouter

from src.users.dao import UserDAO
from src.users.schemas import SUserNotFound, SUserOutput

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_all_users() -> list[SUserOutput]:
    """Get all users."""
    result = await UserDAO.get_all()
    return result


@router.get("/{user_id}", responses={404: {"model": SUserNotFound}})
async def get_user(user_id: int) -> SUserOutput:
    """Get user by id."""
    result = await UserDAO.get_object_or_404(id=user_id)
    return result
