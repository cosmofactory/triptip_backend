from pydantic import BaseModel


class SLikeOutput(BaseModel):
    """Schema for likes output data."""

    id: int
    author_id: int
    trip_id: int
