import uuid

from sqlalchemy import select, and_
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg

from app.models.users_model import User
from app.videos.extractors import extract_video_id


class Video(SQLModel,table=True):
    __tablename__ = "videos"
    db_id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    host_id: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    host_service: str = Field(default="Youtube", sa_column=Column(pg.TEXT, default="Youtube"))
    url: str=Field(nullable=False)
    description: str = Field(default="", nullable=True)
    user_id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False))
    channel_id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=True))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"<Video host_id={self.host_id}, host_service={self.host_service}, user_id={self.user_id}>"

    @property
    def path(self):
        return f"/videos/{self.host_id}"

    def as_data(self):
        return {
            f"{self.host_service}_id": self.host_id,
            "path": self.path,
        }

    @staticmethod
    async def get_or_create(url: str, user_id: uuid.UUID, session):
        host_id = extract_video_id(url)
        if not host_id:
            raise ValueError("Invalid video URL")

        created = False
        try:
            query = select(Video).where(Video.host_id == host_id)
            result = await session.execute(query)
            obj = result.scalar_one()
        except NoResultFound:
            obj = Video(host_id=host_id, user_id=user_id, url=url)
            session.add(obj)
            await session.commit()
            created = True
        except MultipleResultsFound:
            query = select(Video).where(Video.host_id == host_id).limit(1)
            result = await session.execute(query)
            obj = result.scalar_one()

        return obj, created

    # async def update_video_url(self, url: str, session):
    #     host_id = extract_video_id(url)
    #     if not host_id:
    #         return None
    #     self.url = url
    #     self.host_id = host_id
    #     session.add(self)
    #     await session.commit()
    #     return url

    @staticmethod
    async def add_video(url, user_id,session):
        # extract video_id from url
        # video_id = host_id
        # Service API - YouTube / Vimeo / etc
        host_id = extract_video_id(url)
        print(host_id)
        if host_id is None:
            raise Exception("Invalid YouTube Video URL")
        user_exists =  await User.check_exists(user_id, session)
        if user_exists is None:
            raise Exception("Invalid user_id")
        # query = select(Video).where(Video.user_id == user_id)
        query = select(Video).where(and_(Video.host_id == host_id, Video.user_id == user_id))
        print(session, query)
        result = await session.execute(query)
        existing_video = result.scalars().first()
        if existing_video:
            raise Exception("Video already added")
        new_video = Video(host_id=host_id, user_id=user_id, url=url)
        session.add(new_video)
        await session.commit()  # Commit the transaction to save the video
        return new_video