# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlmodel import select
#
# from app.models.subscriptions_model import Subscription
#
#
# async def subscribe_to_channel(user_id: str, channel_id: str, session: AsyncSession):
#     """Subscribe a user to a channel."""
#     # Check if the user is already subscribed to the channel
#     query = select(Subscription).where(Subscription.user_id == user_id, Subscription.channel_id == channel_id)
#     result = await session.execute(query)
#     existing_subscription = result.scalar_one_or_none()
#
#     if existing_subscription:
#         return existing_subscription  # User is already subscribed
#
#     subscription = Subscription(user_id=user_id, channel_id=channel_id)
#     session.add(subscription)
#     await session.commit()
#     return subscription
#
# async def unsubscribe_from_channel(user_id: str, channel_id: str, session: AsyncSession):
#     """Unsubscribe a user from a channel."""
#     query = select(Subscription).where(Subscription.user_id == user_id, Subscription.channel_id == channel_id)
#     result = await session.execute(query)
#     subscription = result.scalar_one_or_none()
#
#     if subscription:
#         await session.delete(subscription)
#         await session.commit()
#         return subscription
#     return None
#
# async def get_subscriptions_for_user(user_id: str, session: AsyncSession):
#     """Get all channels a user is subscribed to."""
#     query = select(Subscription).where(Subscription.user_id == user_id)
#     result = await session.execute(query)
#     return result.scalars().all()
