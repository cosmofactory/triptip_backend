from pydantic import BaseModel, EmailStr


class SUserRegister(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str
    username: str


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
