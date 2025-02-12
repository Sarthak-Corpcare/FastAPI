from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.comments_model import Comment
from app.schemas.comments_schema import CommentCreate, CommentUpdate


async def create_comment(comment_data: CommentCreate, user_id: str, host_id: str, session: AsyncSession):
    comment_data = comment_data.dict()
    comment_data.pop("user_id", None)
    comment_data.pop("host_id", None)
    comment = Comment(**comment_data, user_id=user_id, host_id=host_id)
    session.add(comment)
    await session.commit()
    return comment

async def get_comments_for_video(host_id: str, session: AsyncSession):
    query = select(Comment).where(Comment.host_id == host_id)
    result = await session.execute(query)
    return result.scalars().all()

# async def update_comment(comment_id: str, comment_data: CommentUpdate, session: AsyncSession):
#     """Update an existing comment."""
#     query = select(Comment).where(Comment.id == comment_id)
#     result = await session.execute(query)
#     comment = result.scalar_one_or_none()
#
#     if comment:
#         for key, value in comment_data.dict(exclude_unset=True).items():
#             setattr(comment, key, value)
#         await session.commit()
#         return comment
#     return None

async def delete_the_comment(comment_id: str, session: AsyncSession):
    query = select(Comment).where(Comment.id == comment_id)
    result = await session.execute(query)
    comment = result.scalar_one_or_none()

    if comment:
        await session.delete(comment)
        await session.commit()
        return comment
    return None
