from uuid import UUID
from fastapi import HTTPException, Depends, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_session
from app.dependencies.auth_depends import AccessTokenBearer
from app.models.likes_model import Like
from app.schemas.likes_schema import LikeCreate

like_router = APIRouter()


@like_router.post("/likes/")
async def like_video(like: LikeCreate,session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    user_id = token_data["user"].get("user_id")
    like_data = like.dict()
    provided_user_id = like_data.get('user_id')  # The user_id passed in the request

    # if provided_user_id != user_id:
    #     raise HTTPException(status_code=400, detail="You cannot like on behalf of another user")

    query = select(Like).where(Like.host_id == like_data["host_id"], Like.user_id == user_id)
    result = await session.execute(query)
    existing_like = result.scalar_one_or_none()

    if existing_like:
        raise HTTPException(status_code=400, detail={"status":"Error","Error":"You have already liked this video"})

    # Creating a new like and associate it with the authenticated user
    db_like = Like(**like_data)

    session.add(db_like)
    await session.commit()
    return {"status":"Success","message": "Video liked successfully", "like": db_like,"error":"Null"}


@like_router.get("/likes/video/{host_id}")
async def get_likes_by_video(host_id:str, session: AsyncSession = Depends(get_session)):
    query = select(Like).where(Like.host_id == host_id)
    result = await session.execute(query)
    db_likes = result.scalars().all()
    print("query=", query)
    return {"video_id": host_id, "likes": len(db_likes)}

@like_router.delete("/likes/")
async def unlike_video(like: LikeCreate,session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    user_id = token_data["user"].get("user_id")

    query = select(Like).where(Like.host_id == like.host_id, Like.user_id == user_id)
    result = await session.execute(query)
    db_like = result.scalar_one_or_none()

    if not db_like:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Like not found"})

    await session.delete(db_like)
    await session.commit()
    return {"status":"Success","message": "Video unliked successfully","error":"Null"}
