from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.auth import get_current_user
from src.database.database import SessionDep
from src.settings.enums import HighlightEnum
from src.trips.dao import LocationDAO, RouteDAO, TripDAO
from src.trips.schemas import (
    SDetailedTripOutput,
    SHighlightInput,
    SHighlightOutput,
    SLocationInput,
    SlocationOutput,
    SObjectAlreadyExists,
    SRouteInput,
    SRouteOutput,
    STripInput,
    STripOutput,
    STripUserOutput,
)
from src.trips.services import TripService
from src.users.schemas import SUserOutput
from src.utils.dependencies import Permissions

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("", response_model=list[STripUserOutput])
async def get_trips(db: SessionDep, limit: int = 50) -> list[STripUserOutput]:
    """Get all trips."""
    trips = await TripService.get_trips(db, limit)
    return trips


@router.get("/{trip_id}", response_model=SDetailedTripOutput)
async def get_trip_details(trip_id: int, db: SessionDep) -> SDetailedTripOutput:
    """Get detailed trip information."""
    trip = await TripService.get_trip(db, trip_id)
    return trip


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_400_BAD_REQUEST: {"model": SObjectAlreadyExists}},
)
async def create_trip(
    trip: STripInput, user: Annotated[SUserOutput, Depends(get_current_user)], db: SessionDep
) -> STripOutput:
    """Create a new trip."""
    created_trip = await TripService.create_trip(db, trip, user.id)
    return created_trip


@router.post(
    "/{trip_id}/locations",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_400_BAD_REQUEST: {"model": SObjectAlreadyExists}},
)
async def create_location(
    trip_id: int,
    location: SLocationInput,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> SlocationOutput:
    """
    Create a new location.

    Check if the user is the author of the trip.
    """
    permissions = Permissions(db)
    await permissions.is_author_or_read_only(trip_id, TripDAO, user)
    created_location = await TripService.create_location(db, trip_id, location)
    return created_location


@router.get("/{trip_id}/locations", response_model=list[SlocationOutput])
async def get_locations(
    trip_id: int,
    db: SessionDep,
) -> list[SlocationOutput]:
    """Get all locations for a trip."""
    locations = await TripService.get_locations(db, trip_id)
    return locations


@router.get("/locations/{location_id}/route", response_model=SRouteOutput)
async def get_route(
    location_id: int,
    db: SessionDep,
) -> SRouteOutput:
    """
    Get route for a location.

    Location ID is the origin of the route.
    """
    route = await TripService.get_route(db, location_id)
    return route


@router.post("/locations/{location_id}/route", status_code=status.HTTP_201_CREATED)
async def create_route(
    location_id: int,
    trip: SRouteInput,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> SRouteOutput:
    """
    Create a new route.

    Location ID is the origin of the route.
    Only location author can create a route.
    """
    permissions = Permissions(db)
    await permissions.is_author_or_read_only(location_id, LocationDAO, user)
    route = await TripService.create_route(db, trip, user.id)
    return route


@router.post("/route/{route_id}/highlight", status_code=status.HTTP_201_CREATED)
async def create_highlight_for_route(
    route_id: int,
    highlight: SHighlightInput,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> SRouteOutput:
    """
    Create a new highlight for route.

    Route ID is the origin of the route.
    Only route author can create a highlight.
    """
    permissions = Permissions(db)
    await permissions.is_author_or_read_only(route_id, RouteDAO, user)
    highlight = await TripService.create_highlight(
        db, highlight, HighlightEnum.ROUTE_HIGHLIGHT, route_id
    )
    return highlight


@router.post("/location/{location_id}/highlight", status_code=status.HTTP_201_CREATED)
async def create_highlight_for_location(
    location_id: int,
    highlight: SHighlightInput,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> SRouteOutput:
    """
    Create a new highlight for location.

    Location ID is the origin of the location.
    Only route author can create a highlight.
    """
    permissions = Permissions(db)
    await permissions.is_author_or_read_only(location_id, LocationDAO, user)
    highlight = await TripService.create_highlight(
        db, highlight, HighlightEnum.LOCATION_HIGHLIGHT, location_id
    )
    return highlight


@router.get("/route/{route_id}/highlights", response_model=list[SHighlightOutput])
async def get_route_highlights(
    route_id: int,
    db: SessionDep,
) -> list[SHighlightOutput]:
    """Get all highlights for a route."""
    highlights = await TripService.get_highlights(db, HighlightEnum.ROUTE_HIGHLIGHT, route_id)
    return highlights


@router.get("/location/{location_id}/highlights", response_model=list[SHighlightOutput])
async def get_location_highlights(
    location_id: int,
    db: SessionDep,
) -> list[SHighlightOutput]:
    """Get all highlights for a location."""
    highlights = await TripService.get_highlights(db, HighlightEnum.LOCATION_HIGHLIGHT, location_id)
    return highlights


@router.get("/highlight/{highlight_id}", response_model=SHighlightOutput)
async def get_highlight(
    highlight_id: int,
    db: SessionDep,
) -> SHighlightOutput:
    """Get highlight"""
    highlights = await TripService.get_highlight(db, highlight_id)
    return highlights
