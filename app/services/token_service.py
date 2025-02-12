from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.token_model import RevokedToken
from app.db import get_session


async def add_jti_to_blocklist(jti: str, session):
    # Storing revoked JTI in the database
    revoked_token = RevokedToken(jti=jti)
    session.add(revoked_token)
    await session.commit()

async def is_jti_blocked(jti: str, session):
    # checking if it's in the blocklist
    query = select(RevokedToken).where(RevokedToken.jti == jti)
    result = await session.execute(query)
    return result.scalar_one_or_none() is not None
