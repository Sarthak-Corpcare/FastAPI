from uuid import UUID
from pydantic import BaseModel


class CommentBase(BaseModel):
    host_id: str
    # user_id: UUID
    text: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    text: str

    class Config:
        orm_mode = True
