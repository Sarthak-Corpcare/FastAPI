from datetime import datetime
from sqlmodel import SQLModel, Field, Column
import uuid
import sqlalchemy.dialects.postgresql as pg


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"

    id: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, default=uuid.uuid4))
    user_id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False))  # Subscriber
    channel_id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False))  # Subscribed channel
    subscribed_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Subscription user_id={self.user_id}, channel_id={self.channel_id}>"
