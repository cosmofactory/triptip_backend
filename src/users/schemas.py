from src.dao.schema import OrmBase


class SUserInput(OrmBase):
    """Schema for User input data."""

    email: str
    password: str
    first_name: str | None
    last_name: str | None
    userpic: str | None
    bio: str | None


class SUserOutput(OrmBase):
    """Schema for User output data."""

    id: int
    email: str
    username: str
    first_name: str | None
    last_name: str | None
    userpic: str | None
    bio: str | None
    is_admin: bool


class SShortUserInfo(OrmBase):
    """Schema for User output data."""

    id: int
    email: str
    username: str
    userpic: str | None


class SUserNotFound(OrmBase):
    """Schema for User not found response."""

    detail: str
