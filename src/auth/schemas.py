from pydantic import BaseModel, EmailStr

from src.users.schemas import SUserOutput


class SUserRegister(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str
    username: str
    first_name: str | None = None
    last_name: str | None = None


class SUserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class STokens(BaseModel):
    """Tokens schema."""

    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    """Token data schema."""

    email: str


class Token(BaseModel):
    """Token pair schema."""

    access_token: str
    refresh_token: str | None
    token_type: str
    user_data: SUserOutput


class VerifyTokenInput(BaseModel):
    """Input schema for token verification."""

    token: str


class SPasswordRecoveryRequest(BaseModel):
    """Schema for password recovery request."""

    email: EmailStr


class SPasswordRecovery(BaseModel):
    """Schema for password recovery process."""

    new_password: str
    token: str


class EmailResponse(BaseModel):
    """Email response schema."""

    message: str
    email: EmailStr
    expires_in_hours: int


class PasswordResetResponse(BaseModel):
    """Schema for password reset process."""

    message: str
