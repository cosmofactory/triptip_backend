from pydantic import BaseModel

class SubscriptionOutput(BaseModel):
    """Schema for subscriptions output data."""
    id: int
    follower_id: int
    followee_id: int