# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlmodel import select
#
# from app.models.likes_model import Like
#
#
# async def like_video(user_id: str, video_id: str, session: AsyncSession):
#     """Like a video."""
#     # Check if the user has already liked the video
#     query = select(Like).where(Like.user_id == user_id, Like.video_id == video_id)
#     result = await session.execute(query)
#     existing_like = result.scalar_one_or_none()
#
#     if existing_like:
#         return existing_like  # User already liked the video
#
#     like = Like(user_id=user_id, video_id=video_id)
#     session.add(like)
#     await session.commit()
#     return like
#
# async def unlike_video(user_id: str, video_id: str, session: AsyncSession):
#     """Unlike a video."""
#     query = select(Like).where(Like.user_id == user_id, Like.video_id == video_id)
#     result = await session.execute(query)
#     like = result.scalar_one_or_none()
#
#     if like:
#         await session.delete(like)
#         await session.commit()
#         return like
#     return None
#
# async def get_likes_for_video(video_id: str, session: AsyncSession):
#     """Get all likes for a video."""
#     query = select(Like).where(Like.video_id == video_id)
#     result = await session.execute(query)
#     return result.scalars().all()
