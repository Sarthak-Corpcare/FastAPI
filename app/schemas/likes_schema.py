from uuid import UUID

from pydantic import BaseModel


class LikeBase(BaseModel):
    host_id: str
    # user_id: UUID

class LikeCreate(LikeBase):
    pass

    class Config:
        orm_mode = True