from uuid import UUID
from pydantic import BaseModel

class ChannelBase(BaseModel):
    name: str
    # user_id: UUID

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    name: str

    class Config:
        orm_mode = True
