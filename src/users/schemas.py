from pydantic import BaseModel, ConfigDict


class SUserInput(BaseModel):
    """Schema for User input data."""

    email: str
    password: str
    first_name: str | None
    last_name: str | None
    userpic: str | None
    bio: str | None

    model_config = ConfigDict(from_attributes=True)


class SUserOutput(BaseModel):
    """Schema for User output data."""

    id: int
    email: str
    username: str
    first_name: str | None
    last_name: str | None
    userpic: str | None
    bio: str | None
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class SUserNotFound(BaseModel):
    """Schema for User not found response."""

    detail: str

    model_config = ConfigDict(from_attributes=True)
