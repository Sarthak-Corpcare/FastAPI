# comments_routes.py
from uuid import UUID
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_session
from app.dependencies.auth_depends import AccessTokenBearer
from app.models.comments_model import Comment
from app.schemas.comments_schema import CommentCreate, CommentUpdate
from app.services.comments_service import create_comment, get_comments_for_video, delete_the_comment

comment_router = APIRouter()

@comment_router.post("/comments/")
async def add_comment( comment: CommentCreate, session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    user_id = token_data["user"].get("user_id")
    host_id = comment.host_id
    db_comment = await create_comment(comment, user_id, host_id, session)
    return {"status":"Success","message": "Comment added successfully", "comment": db_comment,"error":"Null"}


@comment_router.get("/comments/video/{host_id}")
async def get_comments_by_video(host_id: str,session: AsyncSession = Depends(get_session)):
    db_comments = await get_comments_for_video(host_id, session)
    if not db_comments:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"No comments found for this video"})
    return db_comments


@comment_router.put("/comments/{comment_id}")
async def update_comment(comment_id: UUID,comment: CommentUpdate,session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    user_id = token_data["user"].get("user_id")
    query = select(Comment).where(Comment.id == comment_id)
    result = await session.execute(query)
    db_comment = result.scalar_one_or_none()

    if not db_comment:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Comment not found"})

    if str(db_comment.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail={"status":"Error","Error":"Not authorized to update this comment"})

    db_comment.text = comment.text
    await session.commit()
    return {"Status":"Success","message": "Comment updated successfully", "comment": db_comment,"error":"Null"}


@comment_router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: UUID, session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())  # Ensure the user is authenticated
):
    user_id = token_data["user"].get("user_id")
    db_comment = await delete_the_comment(comment_id, session)

    if not db_comment:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Comment not found"})

    if str(db_comment.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail={"status":"Error","Error":"Not authorized to delete this comment"})
    return {"status":"Success","message": "Comment deleted successfully","Error":"Null"}