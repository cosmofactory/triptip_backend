from datetime import date, datetime

from pydantic import BaseModel

from src.dao.schema import OrmBase
from src.settings.enums import RegionEnum, VisibilityEnum
from src.users.schemas import SShortUserInfo, SUserOutput


class STripLocationOutput(OrmBase):
    """Location output schema."""

    id: int
    name: str


class SDetailedTripOutput(OrmBase):
    """Detailed Trip output schema."""

    id: int
    name: str
    description: str
    region: RegionEnum
    created_at: datetime
    date_from: date
    date_to: date
    author_id: int
    likes_counter: int
    locations: list[STripLocationOutput]
    visibility: VisibilityEnum


class STripOutput(OrmBase):
    """Trip list output schema."""

    id: int
    name: str
    description: str
    region: RegionEnum
    date_from: date
    date_to: date
    author_id: int
    likes_counter: int
    visibility: VisibilityEnum


class STripLikeOutput(OrmBase):
    """Schema with likes counter and list of users who liked a trip."""

    id: int
    likes_counter: int
    users: list[SUserOutput]


class STripUserOutput(OrmBase):
    """Trip list output schema."""

    id: int
    name: str
    description: str
    region: RegionEnum
    date_from: date
    date_to: date
    author: SShortUserInfo
    visibility: VisibilityEnum


class STripListOutput(OrmBase):
    """Trip list output schema with number of trips."""

    trips: list[STripOutput]
    total_count: int


class STripInput(OrmBase):
    """Create new Trip."""

    name: str
    description: str
    region: RegionEnum
    date_from: date
    date_to: date
    visibility: VisibilityEnum


class SObjectAlreadyExists(BaseModel):
    """Object already exists error."""

    detail: str = "Object already exists"


class SLocationInput(OrmBase):
    """Create new Location."""

    name: str
    description: str
    sequence_id: int


class SlocationOutput(OrmBase):
    """Location output schema."""

    id: int
    name: str
    description: str
    sequence_id: int | None


class SRouteInput(OrmBase):
    """Create new route."""

    description: str
    origin_id: int
    destination_id: int | None = None


class SRouteOutput(OrmBase):
    """Route output schema."""

    id: int
    description: str
    origin_id: int
    destination_id: int | None = None


class SHighlightInput(OrmBase):
    """Create new highlight."""

    name: str
    description: str | None = None


class SHighlightOutput(OrmBase):
    """Highlight output schema."""

    id: int
    name: str
    description: str
    location_id: int | None
    route_id: int | None
