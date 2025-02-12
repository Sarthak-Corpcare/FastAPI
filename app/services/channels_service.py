from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.channels_model import Channel
from app.schemas.channels_schema import ChannelCreate, ChannelUpdate


async def create_channel(channel_data: ChannelCreate, user_id: str, session: AsyncSession):
    channel_data = channel_data.dict()
    channel_data.pop("user_id", None)  # removing user_id if it exist

    channel = Channel(**channel_data, user_id=user_id)

    # channel = Channel(**channel_data.dict(), user_id=user_id)
    session.add(channel)
    await session.commit()
    return channel

async def get_channel_by_id(channel_id: str, session: AsyncSession):
    query = select(Channel).where(Channel.id == channel_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def update_channel(channel_id: str, channel_data: ChannelUpdate, session: AsyncSession):
    query = select(Channel).where(Channel.id == channel_id)
    result = await session.execute(query)
    channel = result.scalar_one_or_none()

    if channel:
        for key, value in channel_data.dict(exclude_unset=True).items():
            setattr(channel, key, value)
        await session.commit()
        return channel
    return None

async def delete_channel(channel_id: str, session: AsyncSession):
    query = select(Channel).where(Channel.id == channel_id)

