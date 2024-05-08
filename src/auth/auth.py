import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.auth.dao import AuthDAO, RefreshTokenDAO
from src.auth.schemas import SUserLogin, SUserRegister, TokenData
from src.settings.config import settings
from src.users.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password: str) -> str:
    """Hash given password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the given password and existing password."""
    return pwd_context.verify(plain_password, hashed_password)


async def hash_user_password(user_data: SUserRegister) -> str:
    """Check if the user with the provided email exists and hash the password."""
    check_existing_user = await AuthDAO.get_one_or_none(email=user_data.email)
    if check_existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists"
        )
    return get_password_hash(user_data.password)


async def authenticate_user(email, password) -> SUserLogin:
    """Check if the user with the provided email and password exists."""
    user = await AuthDAO.get_one_or_none(email=email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


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


async def create_tokens(user: User) -> dict:
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
        secure=False,
        samesite="Lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get the current user with the given token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception from None
    user = await AuthDAO.get_one_or_none(email=token_data.email)
    if not user:
        raise credentials_exception
    return user
