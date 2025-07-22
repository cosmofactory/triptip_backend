from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from src.auth.auth import (
    authenticate_user,
    create_tokens,
    get_current_user,
    register_user,
    request_user_password_recovery,
    resend_verification_email,
    reset_password,
    set_cookies,
    verify_email,
)
from src.auth.dao import AuthDAO
from src.auth.schemas import (
    SPasswordRecovery,
    SPasswordRecoveryRequest,
    SUserRegister,
    Token,
    VerifyTokenInput,
)
from src.database.database import SessionDep
from src.settings.config import settings
from src.users.schemas import SUserOutput

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "User with this email already exists"}},
)
async def register_user_handler(
    user_data: SUserRegister,
    db: SessionDep,
    background_tasks: BackgroundTasks,
):
    """
    Register a new user.

    Check if the user with the provided email already exists.
    If the user does not exist, hash the password and create a new user.
    """

    await register_user(
        db,
        user_data,
        background_tasks,
    )
    return Response(status_code=status.HTTP_201_CREATED)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"}},
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response, db: SessionDep
) -> Token:
    """
    Log in the user.

    If the user with the provided email and password exists, create access and refresh tokens.
    Refresh token will be stored in database.
    Both access and refresh tokens will be added to cookies.
    Return token values.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tokens = await create_tokens(db, user)
    await set_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return Token(**tokens, user_data=user)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"}},
)
async def refresh(request: Request, response: Response, db: SessionDep) -> Token:
    """
    Refresh access token.
    Check if the refresh token is valid and exists in cookies.
    If the refresh token is valid, create new access and refresh tokens.
    Both access and refresh tokens will be added to cookies.
    Return token values.
    """
    wrong_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
    )
    if refresh_token := request.cookies.get("refresh_token"):
        try:
            payload = jwt.decode(
                refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
        except JWTError:
            raise wrong_credentials from None
        user = await AuthDAO.get_one_or_none(db, email=email)
        new_tokens = await create_tokens(db, user)
        await set_cookies(response, new_tokens.get("access_token"), new_tokens.get("refresh_token"))
        return Token(**new_tokens, user_data=user)
    else:
        raise wrong_credentials


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    """Log out the user. Remove access and refresh tokens from cookies."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@router.post("/verify", status_code=status.HTTP_200_OK, response_model=Token)
async def verify_email_handler(data: VerifyTokenInput, session: SessionDep) -> Token:
    return await verify_email(data.token, session)


@router.post(
    "/resend_verification",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=dict,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "User is already verified"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Email sending limit exceeded"},
    },
)
async def resend_verification_email_handler(
    current_user: Annotated[SUserOutput, Depends(get_current_user)],
    background_tasks: BackgroundTasks,
    db: SessionDep,
) -> dict:
    """Resend verification email for authenticated user."""
    await resend_verification_email(
        current_user,
        background_tasks,
        db,
    )
    return {
        "message": "Verification email sent successfully",
        "email": current_user.email,
        "expires_in_hours": settings.EMAIL_VERIFICATION_EXPIRATION_HOURS,
    }


@router.post(
    "/request_password_recovery",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Email sending limit exceeded"},
    },
)
async def request_password_recovery_handler(
    request_data: SPasswordRecoveryRequest,
    background_tasks: BackgroundTasks,
    db: SessionDep,
) -> dict:
    """
    Request password recovery for a user.
    """
    await request_user_password_recovery(request_data.email, background_tasks, db)
    return {
        "message": "Password recovery email sent successfully",
        "email": request_data.email,
        "expires_in_hours": settings.PASSWORD_RECOVERY_EXPIRATION_HOURS,
    }


@router.post(
    "/reset_password",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid token"},
    },
)
async def reset_password_handler(data: SPasswordRecovery, session: SessionDep) -> dict:
    """
    Reset password with given token.
    """
    await reset_password(data, session)
    return {"message": "Password reset successfully"}
