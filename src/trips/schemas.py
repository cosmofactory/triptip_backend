from datetime import date

from pydantic import BaseModel, ConfigDict

from src.settings.enums import RegionEnum


class STripLocationOutput(BaseModel):
    """Location output schema."""

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class SDetailedTripOutput(BaseModel):
    """Detailed Trip output schema."""

    id: int
    name: str
    description: str
    region: RegionEnum
    date_from: date
    date_to: date
    author_id: int
    locations: list[STripLocationOutput]

    model_config = ConfigDict(from_attributes=True)


class STripOutput(BaseModel):
    """Trip list output schema."""

    id: int
    name: str
    description: str
    region: RegionEnum
    date_from: date
    date_to: date
    author_id: int

    model_config = ConfigDict(from_attributes=True)


class STripListOutput(BaseModel):
    """Trip list output schema with number of trips."""

    trips: list[STripOutput]
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class STripInput(BaseModel):
    """Create new Trip."""

    name: str
    description: str
    region: RegionEnum
    date_from: date
    date_to: date


class SObjectAlreadyExists(BaseModel):
    """Object already exists error."""

    detail: str = "Object already exists"


class SLocationInput(BaseModel):
    """Create new Location."""

    name: str
    description: str


class SlocationOutput(BaseModel):
    """Location output schema."""

    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class SRouteInput(BaseModel):
    """Create new route."""

    name: str
    description: str
    origin_id: int
    destination_id: int


class SRouteOutput(BaseModel):
    """Route output schema."""

    id: int
    name: str
    description: str
    origin_id: int
    destination_id: int

    model_config = ConfigDict(from_attributes=True)
