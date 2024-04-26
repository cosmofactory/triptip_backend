from pydantic import BaseModel, ConfigDict


class SUserInput(BaseModel):
    """Schema for User input data."""

    email: str
    password: str
    userpic: str

    model_config = ConfigDict(from_attributes=True)


class SUserOutput(BaseModel):
    """Schema for User output data."""

    id: int
    email: str
    username: str
    userpic: str
    bio: str

    model_config = ConfigDict(from_attributes=True)
