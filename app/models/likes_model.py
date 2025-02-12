from datetime import datetime
from sqlalchemy import String
from sqlmodel import SQLModel, Field, Column
import uuid
import sqlalchemy.dialects.postgresql as pg

class Like(SQLModel, table=True):
    __tablename__ = "likes"

    id: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4))
    user_id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False))  # User who liked the video
    host_id: str =Field(sa_column=Column(String, nullable=False)) # Video being liked
    liked_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Like user_id={self.user_id}, video_id={self.video_id}>"
