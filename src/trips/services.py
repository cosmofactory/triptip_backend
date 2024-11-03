import logfire
from sqlalchemy.ext.asyncio import AsyncSession

from src.settings.enums import HighlightEnum
from src.trips.dao import HighlightDAO, LocationDAO, RouteDAO, TripDAO
from src.trips.schemas import (
    SDetailedTripOutput,
    SHighlightInput,
    SHighlightOutput,
    SLocationInput,
    SRouteInput,
    STripInput,
    STripOutput,
)


class TripService:
    """Service layer for Trip."""

    @staticmethod
    @logfire.instrument()
    async def get_trips(db: AsyncSession, limit: int) -> list[STripOutput]:
        """Get list of trips."""
        trips = await TripDAO.get_all_trips(db, limit)
        return trips

    @staticmethod
    async def get_trip(db: AsyncSession, trip_id: int) -> SDetailedTripOutput:
        """Get detailed trip information."""
        trip = await TripDAO.get_object_or_404(db, id=trip_id)
        return trip

    @staticmethod
    async def create_trip(db: AsyncSession, trip_data: STripInput, user_id: int) -> STripOutput:
        """Create a new trip."""
        trip_data = trip_data.model_dump()
        trip_data["author_id"] = user_id
        created_trip = await TripDAO.create(db, **trip_data)
        return created_trip

    @staticmethod
    async def create_location(db: AsyncSession, trip_id: int, location_data: SLocationInput):
        """Create a new location."""
        location_data = location_data.model_dump()
        location_data["trip_id"] = trip_id
        created_location = await LocationDAO.create(db, **location_data)
        return created_location

    @staticmethod
    async def get_locations(db: AsyncSession, trip_id: int):
        """Get list of locations for a trip."""
        locations = await LocationDAO.get_all(db, trip_id=trip_id)
        return locations

    @staticmethod
    async def get_route(db: AsyncSession, location_id: int):
        """Get route between two locations."""
        route = await RouteDAO.get_object_or_404(db, origin_id=location_id)
        return route

    @staticmethod
    async def create_route(db: AsyncSession, route_data: SRouteInput, user_id: int):
        """Create a new route."""
        route_data = route_data.model_dump()
        route_data["author_id"] = user_id
        created_route = await RouteDAO.create(db, **route_data)
        return created_route

    @staticmethod
    async def create_highlight(
        db: AsyncSession,
        highlight_data: SHighlightInput,
        highlight_entity: HighlightEnum,
        entity_id: int,
    ):
        """Create a new highlight."""
        highlight_data = highlight_data.model_dump()
        match highlight_entity:
            case HighlightEnum.ROUTE_HIGHLIGHT:
                highlight_data["route_id"] = entity_id
            case HighlightEnum.LOCATION_HIGHLIGHT:
                highlight_data["location_id"] = entity_id
            case _:
                raise ValueError("Invalid highlight entity type")

        created_highlight = await HighlightDAO.create(db, **highlight_data)
        return created_highlight

    @staticmethod
    async def get_highlights(
        db: AsyncSession, highlight_entity: HighlightEnum, entity_id: int
    ) -> list[SHighlightOutput]:
        """Get list of highlight for route or location."""
        match highlight_entity:
            case HighlightEnum.ROUTE_HIGHLIGHT:
                highlight = await HighlightDAO.get_all(db, route_id=entity_id)
            case HighlightEnum.LOCATION_HIGHLIGHT:
                highlight = await HighlightDAO.get_all(db, location_id=entity_id)
            case _:
                raise ValueError("Invalid highlight entity type")

        return highlight

    @staticmethod
    async def get_highlight(db: AsyncSession, highlight_id: int) -> SHighlightOutput:
        """Get highlight information."""
        highlight = await HighlightDAO.get_object_or_404(db, id=highlight_id)

        return highlight
