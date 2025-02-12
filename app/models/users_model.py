from argon2 import PasswordHasher
from fastapi import HTTPException, Depends
import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import SQLModel, Field, Column, Session
import sqlalchemy.dialects.postgresql as pg
from app.users import security
from app.users.validator import email_validate

from sqlmodel.ext.asyncio.session  import AsyncSession

from app.db import get_session

Base = declarative_base()
from app.users.security import generate_hash, verify_hash

class User(SQLModel,table=True):
    __tablename__= "users"
    user_id:UUID=Field(sa_column=Column(pg.UUID,nullable=False,primary_key=True,default=uuid.uuid4))
    email:str
    password: str = Field(sa_column=Column(TEXT))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"<User email={self.email} , user_id={self.user_id}>"

    async def set_password(self,pw,commit=False):
        pw_hash=await generate_hash(pw)
        self.password=pw_hash
        if commit:
            await self.save()
        return True

    async def verify_password(self,pw_str): #pw plain text password
        pw_hash = self.password
        print(f"Hashed password: {pw_hash}")
        print(f"Plain-text password: {pw_str}")
        verified, _ = await verify_hash(self,pw_hash,pw_str)
        print(f"Password verification result: {verified}")
        return verified

    @staticmethod
    async def create_user(email: str, password: str, session: Session):
    # Check if user already exists

        new_user =  User(email=email)
        await new_user.set_password(password)

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user

    @staticmethod
    async def check_exists(user_id,session):
        query=select(User).where(user_id==user_id)
        result =  await session.execute(query)
        user = result.scalars().first()
        return user is not  None

    @staticmethod
    async def by_user_id(user_id=None, session: Session = Depends(get_session)):
        if user_id is None:
            return None
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()
        if user is None:
            return None
        return user
