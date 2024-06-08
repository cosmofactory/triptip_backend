from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.auth import get_current_user
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
async def get_trips(limit: int = 50) -> list[STripOutput]:
    """Get all trips."""
    trips = await TripService.get_trips(limit)
    return trips


@router.get("/{trip_id}", response_model=SDetailedTripOutput)
async def get_trip_details(trip_id: int) -> SDetailedTripOutput:
    """Get detailed trip information."""
    trip = await TripService.get_trip(trip_id)
    return trip


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_400_BAD_REQUEST: {"model": SObjectAlreadyExists}},
)
async def create_trip(
    trip: STripInput, user: Annotated[SUserOutput, Depends(get_current_user)]
) -> STripOutput:
    """Create a new trip."""
    created_trip = await TripService.create_trip(trip, user.id)
    return created_trip


@router.post(
    "/{trip_id}/locations",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_400_BAD_REQUEST: {"model": SObjectAlreadyExists}},
)
async def create_location(
    trip_id: int, location: SLocationInput, user: Annotated[SUserOutput, Depends(get_current_user)]
) -> SlocationOutput:
    """Create a new location."""
    created_location = await TripService.create_location(trip_id, location, user.id)
    return created_location


@router.get("/{trip_id}/locations", response_model=list[SlocationOutput])
async def get_locations(trip_id: int) -> list[SlocationOutput]:
    """Get all locations for a trip."""
    locations = await TripService.get_locations(trip_id)
    return locations
