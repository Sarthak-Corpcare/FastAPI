from datetime import datetime

from sqlmodel import SQLModel, Field, Column
import uuid
import sqlalchemy.dialects.postgresql as pg


class Channel(SQLModel, table=True):
    __tablename__ = "channels"
    id: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4))
    name: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    user_id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False))  # The creator of the channel
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Channel name={self.name}, user_id={self.user_id}>"
