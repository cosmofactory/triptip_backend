from src.dao.base import BaseDAO
from src.subscriptions.models import Subscriptions


class SubscriptionDAO(BaseDAO):
    """DAO for Subscriptions limits model"""

    model = Subscriptions
