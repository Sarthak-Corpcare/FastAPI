from uuid import UUID

from pydantic import BaseModel


class SubscriptionBase(BaseModel):
    # user_id: UUID
    channel_id: UUID

class SubscriptionCreate(SubscriptionBase):
    pass

    class Config:
        orm_mode = True

