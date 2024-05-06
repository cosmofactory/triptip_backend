from fastapi import APIRouter, HTTPException, status

from src.auth.auth import get_password_hash, verify_password
from src.auth.dao import AuthDAO
from src.auth.schemas import STokens, SUserLogin, SUserRegister
from src.settings.config import security

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "User with this email already exists"}},
)
async def register_user(user_data: SUserRegister):
    """
    Register a new user.

    Check if the user with the provided email already exists.
    If the user does not exist, hash the password and create a new user.
    """
    check_existing_user = await AuthDAO.get_one_or_none(email=user_data.email)
    if check_existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists"
        )
    hashed_password = get_password_hash(user_data.password)
    await AuthDAO.create(
        email=user_data.email, password=hashed_password, username=user_data.username
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"}},
)
async def login_user(login_data: SUserLogin) -> STokens:
    """Login a user."""
    user = await AuthDAO.get_one_or_none(email=login_data.email)
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = security.create_access_token(uid=user.id)
    refresh_token = security.create_refresh_token(uid=user.id)

    return STokens(access_token=access_token, refresh_token=refresh_token)
