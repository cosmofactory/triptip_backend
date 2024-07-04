from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.auth import get_current_user
from src.auth.dependencies import is_author_or_read_only
from src.database.database import SessionDep
from src.trips.dao import TripDAO
from src.trips.schemas import (
    SDetailedTripOutput,
    SLocationInput,
    SlocationOutput,
    SObjectAlreadyExists,
    STripInput,
    STripOutput,
)
from src.trips.services import TripService
from src.users.schemas import SUserOutput

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("", response_model=list[STripOutput])
async def get_trips(db: SessionDep, limit: int = 50) -> list[STripOutput]:
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
    await is_author_or_read_only(db, trip_id, TripDAO, user)
    created_location = await TripService.create_location(db, trip_id, location, user.id)
    return created_location


@router.get("/{trip_id}/locations", response_model=list[SlocationOutput])
async def get_locations(
    trip_id: int,
    db: SessionDep,
) -> list[SlocationOutput]:
    """Get all locations for a trip."""
    locations = await TripService.get_locations(db, trip_id)
    return locations
