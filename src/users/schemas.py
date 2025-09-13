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
    followings_counter: int
    is_admin: bool
    is_verified: bool


class SShortUserInfo(OrmBase):
    """Schema for User output data."""

    id: int
    email: str
    username: str
    userpic: str | None
    followings_counter: int


class SUserSubscriptionOutput(OrmBase):
    """
    Schema for current User subscription output data.

    Followings counter and list of those current user is subscribed to.
    """

    id: int
    followings_counter: int
    users: list[SUserOutput]


class SUserNotFound(OrmBase):
    """Schema for User not found response."""

    detail: str
