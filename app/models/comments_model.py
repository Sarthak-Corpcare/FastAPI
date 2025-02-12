from datetime import datetime
from sqlmodel import SQLModel, Field, Column
import uuid
import sqlalchemy.dialects.postgresql as pg

class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4))
    user_id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False))  # Commenting user
    host_id: str  # Video being commented on
    text: str = Field(sa_column=Column(pg.TEXT, nullable=False))  # Comment content
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Comment user_id={self.user_id}, video_id={self.video_id}, text={self.text}>"
