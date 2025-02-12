from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.dependencies.auth_depends import AccessTokenBearer
from app.schemas.channels_schema import ChannelCreate, ChannelUpdate
from app.services.channels_service import create_channel, get_channel_by_id, update_channel, delete_channel

channel_router = APIRouter()

@channel_router.post("/channels/")
async def create_channel_route(channel: ChannelCreate,session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    user_id = token_data["user"].get("user_id")
    db_channel = await create_channel(channel, user_id, session)
    return {"status":"Success","message": "Channel created successfully", "channel": db_channel,"error":"Null"}


@channel_router.get("/channels/{channel_id}")
async def get_channel_route(channel_id: str,session: AsyncSession = Depends(get_session)):
    db_channel = await get_channel_by_id(channel_id, session)
    if not db_channel:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Channel not found"})
    return db_channel


@channel_router.put("/channels/{channel_id}")
async def update_channel_route(channel_id: str,channel: ChannelUpdate, session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    user_id = token_data["user"].get("user_id")
    db_channel = await get_channel_by_id(channel_id, session)
    if not db_channel:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Channel not found"})

    if str(db_channel.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this channel")
    updated_channel = await update_channel(channel_id, channel, session)

    if updated_channel:
        return {"message": "Channel updated successfully", "channel": updated_channel}
    else:
        raise HTTPException(status_code=400, detail={"status":"error","error":"Failed to update channel"})


@channel_router.delete("/channels/{channel_id}")
async def delete_channel_route(channel_id: str,session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    user_id = token_data["user"].get("user_id")
    db_channel = await get_channel_by_id(channel_id, session)
    if not db_channel:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Channel not found"})

    # Check if the logged-in user is the owner of the channel
    if str(db_channel.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail={"status":"Error","Error":"Not authorized to delete this channel"})

    await delete_channel(channel_id, session)
    return {"status":"Success","message": "Channel deleted successfully","error":"Null"}
