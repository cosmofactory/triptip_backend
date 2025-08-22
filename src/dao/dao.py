"""DAO module."""
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dao import AuthDAO, RefreshTokenDAO
from src.emails.dao import EmailDAO
from src.trips.dao import HighlightDAO, LocationDAO, RouteDAO, TripDAO
from src.users.dao import UserDAO


class DAO:
    """Class for accessing all the DAOs."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth = AuthDAO(self.db)
        self.refresh_token = RefreshTokenDAO(self.db)
        self.user = UserDAO(self.db)
        self.trip = TripDAO(self.db)
        self.location = LocationDAO(self.db)
        self.route = RouteDAO(self.db)
        self.highlight = HighlightDAO(self.db)
        self.email = EmailDAO(self.db)
