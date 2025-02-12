import uuid
from typing import List
from uuid import UUID
from fastapi import HTTPException, Depends, APIRouter, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_session
from app.dependencies.auth_depends import AccessTokenBearer
from app.models.subscriptions_model import Subscription
from app.models.users_model import User
from app.schemas.subscriptions_schema import SubscriptionCreate

subscription_router = APIRouter()

@subscription_router.post("/subscriptions/")
async def subscribe_to_channel(subscription: SubscriptionCreate,session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    user_id = token_data["user"].get("user_id")
    # provided_user_id
    # subs_data= subscription.dict()
    # provided_user_id = subs_data.get('user_id')

    # if str(Subscription.user_id) != str(user_id):
    #     raise HTTPException(status_code=403, detail="Not authorized to subscribe on behalf of another user")
    # Checking if the user is already subscribed to the channel
    query = select(Subscription).where(Subscription.user_id == user_id,Subscription.channel_id == subscription.channel_id)
    result = await session.execute(query)
    existing_subscription = result.scalar_one_or_none()

    if existing_subscription:
        raise HTTPException(status_code=400, detail={"status":"Error","Error":"You are already subscribed to this channel"})

    subscription_data = subscription.dict()
    subscription_data.pop("user_id", None)

    db_subscription = Subscription(**subscription_data, user_id=user_id)
    session.add(db_subscription)
    await session.commit()

    return {"status":"success","message": "User subscribed successfully", "subscription": db_subscription,"error":"Null"}


@subscription_router.get("/subscriptions/user/{user_id}")
async def get_user_subscriptions(user_id: UUID,session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    if str(user_id) != str(token_data["user"].get("user_id")):
        raise HTTPException(status_code=403, detail={"status":"Error","Error":"You can only view your own subscriptions"})

    query = select(Subscription).where(Subscription.user_id == user_id)
    result = await session.execute(query)
    db_subscriptions = result.scalars().all()

    if not db_subscriptions:
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"No subscriptions found for this user"})

    channel_ids = [sub.channel_id for sub in db_subscriptions]
    return {"user_id": user_id, "subscriptions": channel_ids}


@subscription_router.get("/subscriptions/{channel_id}",response_model=List[User])
async def get_all_subscribers(channel_id:uuid.UUID, session: AsyncSession=Depends(get_session)):
    query=select(User).join(Subscription,Subscription.user_id==User.user_id).where(Subscription.channel_id==channel_id)

    result=await session.execute(query)
    subscribers=result.scalars().all()

    if not subscribers:
        raise HTTPException(status_code=404,detail={"status":"Error","Error":"No Subscribers found for this channel"})
    return subscribers



@subscription_router.delete("/subscriptions/")
async def unsubscribe_from_channel(subscription: SubscriptionCreate,session: AsyncSession = Depends(get_session),token_data: dict = Depends(AccessTokenBearer())):
    user_id = token_data["user"].get("user_id")
    # query = select(Subscription).where(Subscription.user_id == user_id,Subscription.channel_id == subscription.channel_id)
    delete_query = delete(Subscription).where(Subscription.user_id == user_id, Subscription.channel_id == subscription.channel_id)
    result = await session.execute(delete_query)
    await session.commit()

    if result.rowcount == 0:  # rowcount tells how many rows were deleted
        raise HTTPException(status_code=404, detail={"status":"Error","Error":"Subscription not found"})

    return {"status":"Success","message": "User unsubscribed successfully","error":"null"}