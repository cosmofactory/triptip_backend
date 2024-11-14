from pydantic import BaseModel, ConfigDict


class OrmBase(BaseModel):
    """Base schema for ORM models."""

    model_config = ConfigDict(from_attributes=True)
