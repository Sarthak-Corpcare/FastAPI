import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.videos.extractors import extract_video_id
from app.models.videos_model import Video
from app.schemas.videos_schema import VideoCreateSchema, VideoUpdateSchema
from app.dependencies.auth_depends import AccessTokenBearer

router = APIRouter()

@router.post("/videos")
async def add_video(
    video: VideoCreateSchema,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer())
):
    try:
        user_id = token_data["user"].get("user_id")

        # Adding the video using the model's static method
        new_video = await Video.add_video(url=video.url, user_id=user_id, session=session)
        return {"status": "Success","message": "Video added successfully", "video": new_video,"error":"null"}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"status":"Error","Error":str(e)})


@router.get("/videos/{user_id}")
async def get_videos_by_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer())
):
    # Ensuring the authenticated user is requesting their own videos
    # if str(user_id) != str(token_data["user"].get("user_id")):
    #     raise HTTPException(status_code=403, detail="You can only view your own videos")

    query = select(Video).where(Video.user_id == user_id)
    result = await session.execute(query)
    videos = result.scalars().all()

    if not videos:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"No videos found for this user"})

    return {"videos": videos}

@router.post("/create", response_model=dict)
async def video_create(
    video: VideoCreateSchema,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer())
):
    # Extract host ID
    host_id = extract_video_id(video.url)
    if not host_id:
        raise HTTPException(status_code=400, detail={"status":"Error","Error":"Invalid video URL: Could not extract host_id."})

    user_id = token_data["user"].get("user_id")

    #  Check if the user has already added this video
    existing_video = await session.execute(
        select(Video).where(Video.url == video.url, Video.user_id == user_id)
    )
    video_obj = existing_video.scalar_one_or_none()

    if video_obj:
        raise HTTPException(status_code=400, detail={"status":"Error","Error":f"{video.url} has already been added to your account."})

    new_video = Video(
        url=video.url,
        user_id=user_id,
        host_id=host_id,
        channel_id=video.channel_id,
        description=video.description
    )
    session.add(new_video)
    await session.commit()
    await session.refresh(new_video)

    return {"status": "Success","message": "Video added successfully","video": new_video.as_data(),"error":"null"}

@router.get("/", response_model=list)
async def video_list(session: AsyncSession = Depends(get_session)):
    query = select(Video).limit(100)
    result = await session.execute(query)
    videos = result.scalars().all()
    return videos


@router.get("/v/{host_id}", response_model=dict)
async def video_detail(
    host_id: str,
    session: AsyncSession = Depends(get_session)
):
    query = select(Video).where(Video.host_id == host_id)
    result = await session.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Video not found"})

    return video.as_data()


@router.put("/videos/{host_id}")
async def update_video(
    host_id: str,
    video_update: VideoUpdateSchema,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer())
):
    user_id = token_data["user"].get("user_id")

    query = select(Video).where(Video.host_id == host_id)
    result = await session.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Video not found"})

    if str(video.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail={"status":"Error","Error":"You can only update your own videos"})

    for key, value in video_update.dict(exclude_unset=True).items():
        setattr(video, key, value)

    await session.commit()
    await session.refresh(video)

    return {"status":"success","message": "Video updated successfully", "video": video.as_data(),"error":"null"}


@router.delete("/videos/{host_id}")
async def delete_video(
    host_id: str,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer())
):
    user_id = token_data["user"].get("user_id")

    query = select(Video).where(Video.host_id == host_id)
    result = await session.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Video not found"})

    if str(video.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail={"status":"Error","Error":"You can only delete your own videos"})

    await session.delete(video)
    await session.commit()

    return {"status":"Success","message": "Video Deleted Successfully","error":"Null"}