from sqlmodel import SQLModel, Field
import datetime

class RevokedToken(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    jti: str = Field(unique=True, index=True)  # Unique Token ID (JTI)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
