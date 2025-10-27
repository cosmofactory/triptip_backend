from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.auth import get_current_user
from src.comments.dao import CommentDAO
from src.comments.schemas import SCommentInput, SCommentOutput
from src.comments.service import CommentService
from src.database.database import SessionDep
from src.likes.schemas import SLikeOutput
from src.likes.service import LikeService
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
    STripLikeOutput,
    STripOutput,
    STripUserOutput,
)
from src.trips.services import TripService
from src.users.schemas import SUserOutput
from src.users.service import UserService
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


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: int,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> None:
    """
    Delete an existing trip.
    Soft deletion is implemented for the trip.

    Only trip author can delete a trip.
    """
    permissions = Permissions(db)
    await permissions.is_author_or_read_only(trip_id, TripDAO, user)
    await TripService.delete_trip(db, trip_id)
    return None


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


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> None:
    """
    Delete an existing location.

    Only location author both can create and delete a location.
    """
    permissions = Permissions(db)
    await permissions.is_author_or_read_only(location_id, LocationDAO, user)
    await TripService.delete_location(db, location_id)
    return None


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


@router.delete(
    "/route/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_route(
    route_id: int,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> None:
    """
    Delete an existing route.

    Only route author both can create and delete a route.
    """
    permissions = Permissions(db)
    await permissions.is_author_or_read_only(route_id, RouteDAO, user)
    await TripService.delete_route(db, route_id)
    return None


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


@router.post(
    "/{trip_id}/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=SCommentOutput,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User is not authorized"},
        status.HTTP_404_NOT_FOUND: {"description": "Trip not found"},
    },
)
async def create_comment(
    trip_id: int,
    comment: SCommentInput,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> SCommentOutput:
    """Create a new comment under the trip record."""
    trip = await TripService.get_trip(db, trip_id)
    created_comment = await CommentService.create_comment(db, trip.id, user.id, comment)
    return created_comment


@router.get(
    "/{trip_id}/comments",
    response_model=list[SCommentOutput],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Trip not found"},
    },
)
async def get_comments(
    trip_id: int,
    db: SessionDep,
) -> list[SCommentOutput]:
    """Get all comments under the trip record."""
    trip = await TripService.get_trip(db, trip_id)

    comments = await CommentService.get_comments(db, trip.id)
    return comments


@router.delete(
    "/{trip_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User is not authorized"},
        status.HTTP_403_FORBIDDEN: {"description": "User is not the author of the comment"},
        status.HTTP_404_NOT_FOUND: {"description": "Comment not found"},
    },
)
async def delete_comment(
    trip_id: int,
    comment_id: int,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> None:
    """
    Delete an existing comment under the trip.

    Only comment author can delete a comment.
    """
    await TripService.get_trip(db, trip_id=trip_id)

    permissions = Permissions(db)
    await permissions.is_author_or_read_only(comment_id, CommentDAO, user)
    await CommentService.delete_comment(db, comment_id)
    return None


@router.post(
    "/{trip_id}/like",
    status_code=status.HTTP_201_CREATED,
    response_model=SLikeOutput,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User is not authorized"},
        status.HTTP_404_NOT_FOUND: {"description": "Trip not found"},
    },
)
async def post_like(
    trip_id: int,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> SLikeOutput:
    """Like current trip."""
    trip = await TripService.get_trip(db, trip_id)
    posted_like = await LikeService.leave_like(
        db,
        trip_id=trip.id,
        author_id=user.id,
    )
    return posted_like


@router.get(
    "/{trip_id}/like",
    status_code=status.HTTP_200_OK,
    response_model=STripLikeOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Trip not found"},
    },
)
async def get_trip_likes(
    trip_id: int,
    db: SessionDep,
) -> STripLikeOutput:
    """Get all users and number of users who liked current trip."""
    trip = await TripService.get_trip(db, trip_id)
    users = await UserService.get_all_related_users(
        db=db,
        type_id=trip.id,
        relation_type="like",
    )
    likes_counter = await UserService.get_related_quantity(
        db=db,
        type_id=trip.id,
        relation_type="like",
    )
    return STripLikeOutput(
        id=trip.id,
        likes_counter=likes_counter,
        users=users,
    )


@router.delete(
    "/{trip_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User is not authorized"},
        status.HTTP_404_NOT_FOUND: {"description": "Trip not found"},
    },
)
async def unlike_trip(
    trip_id: int,
    user: Annotated[SUserOutput, Depends(get_current_user)],
    db: SessionDep,
) -> None:
    """Unlike current trip."""
    trip = await TripService.get_trip(db, trip_id=trip_id)

    await LikeService.discard_like(db, user.id, trip.id)
    return None
