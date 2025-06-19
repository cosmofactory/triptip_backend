import datetime
from typing import Annotated, Literal

import logfire
from fastapi import BackgroundTasks, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dao import AuthDAO, RefreshTokenDAO
from src.auth.schemas import SUserLogin, SUserRegister, Token, TokenData
from src.database.database import get_db
from src.emails.service import render_verification_email, send_email
from src.settings.config import settings
from src.users.dao import UserDAO
from src.users.models import User
from src.users.schemas import SUserOutput
from src.utils.exceptions import (
    InvalidTokenPayloadException,
    InvalidTokenTypeException,
    TokenExpiredException,
    UserNotFoundException,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password: str) -> str:
    """Hash given password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the given password and existing password."""
    return pwd_context.verify(plain_password, hashed_password)


@logfire.instrument()
async def check_user_exists(db: AsyncSession, email: str) -> bool:
    check_existing_user = await AuthDAO.get_one_or_none(db, email=email)
    if check_existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists"
        )


async def hash_user_password(user_data: SUserRegister) -> str:
    return get_password_hash(user_data.password)


@logfire.instrument()
async def authenticate_user(db: AsyncSession, email, password) -> SUserLogin:
    """Check if the user with the provided email and password exists."""
    user = await AuthDAO.get_one_or_none(db, email=email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


@logfire.instrument()
def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    """Create access token with the given data and expiration time."""
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@logfire.instrument()
def create_refresh_token(data: dict, expires_delta: datetime.timedelta | None = None):
    """Create refresh token with the given data and expiration time."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@logfire.instrument()
async def create_tokens(db: AsyncSession, user: User) -> dict:
    """
    Call the create_access_token and create_refresh_token.

    Save the refresh token to the database for further use.
    """
    access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token_expires = datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    await RefreshTokenDAO.create(
        db,
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.datetime.now(datetime.timezone.utc) + refresh_token_expires,
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


async def set_cookies(response: Response, access_token: str, refresh_token: str):
    """Set the access token and refresh token as cookies."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )


@logfire.instrument()
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db=Depends(get_db)
) -> SUserOutput:
    """Get the current user with the given token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception from None
    user = await AuthDAO.get_one_or_none(db, email=token_data.email)
    if not user:
        raise credentials_exception
    return SUserOutput.model_validate(user)


@logfire.instrument()
def create_email_verification_token(
    email: str,
    expires_delta: datetime.timedelta = datetime.timedelta(
        hours=settings.EMAIL_VERIFICATION_EXPIRATION_HOURS
    ),
) -> str:
    """Create a token for email verification."""
    payload = {
        "sub": email,
        "verify": True,
        "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)


@logfire.instrument()
async def send_verification_email(email: str, token: str) -> None:
    """Send email with the verification token."""
    verification_link = f"{settings.VERIFICATION_URL}/{token}"
    email_body = render_verification_email(email, verification_link)
    await send_email(email, f"Email Verification for {settings.PROJECT_NAME}", email_body)


@logfire.instrument()
async def register_user(
    db: AsyncSession, user_data: SUserRegister, background_tasks: BackgroundTasks
) -> SUserOutput:
    """Register a new user."""
    await check_user_exists(db, user_data.email)
    hashed_password = await hash_user_password(user_data)
    await AuthDAO.create(
        db, email=user_data.email, password=hashed_password, username=user_data.username
    )
    token = create_email_verification_token(user_data.email)
    background_tasks.add_task(
        send_verification_email,
        user_data.email,
        token,
    )


@logfire.instrument()
async def resend_verification_email(
    email: str, db: AsyncSession, background_tasks: BackgroundTasks
) -> None:
    """Resend the verification email.

    Check is user exists and is not verified.
    Then send verification email.
    """
    user = await AuthDAO.get_one_or_none(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist",
        )
    if user.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already verified",
        )
    verification_token = create_email_verification_token(email)
    background_tasks.add_task(
        send_verification_email,
        email,
        verification_token,
    )
    return None


def verify_token(token: str, payload_value: Literal["reset", "verify"]) -> str:
    """Verify token and extract email from it."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        if not payload.get(payload_value):
            raise InvalidTokenTypeException
        email = payload.get("sub")
        if email is None:
            raise InvalidTokenPayloadException
        return email
    except ExpiredSignatureError as e:
        raise TokenExpiredException from e
    except InvalidTokenError as e:
        raise InvalidTokenTypeException from e


@logfire.instrument()
async def verify_email(token: str, session: AsyncSession) -> Token:
    """
    Verify the email with the given token and login user.

    Update user in database in case of successful verification.
    """
    email = verify_token(token, "verify")

    user = await UserDAO.get_one_or_none(session, email=email)
    user_model = SUserOutput.model_validate(user)
    if not user:
        raise UserNotFoundException

    user_model.is_verified = True
    await UserDAO.update(session, user_model.id, **user_model.model_dump())
    tokens = await create_tokens(session, user)
    return Token(**tokens, user_data=user_model)
