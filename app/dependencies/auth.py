import datetime
from jose import jwt,ExpiredSignatureError
from fastapi import Depends, HTTPException,Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from passlib.context import CryptContext
import config
from config import Settings
from app.models.users_model import User
from app.db import get_session

pwd_context = CryptContext(schemes=["argon2"])
settings=Settings()

async def authenticate(email,password,session: AsyncSession=Depends(get_session)):
    try:
        query=select(User).where(User.email==email)
        result =  await session.execute(query)
        user_obj = result.scalar_one_or_none()
    except Exception as e:
        user_obj = None
    if user_obj is None:
        print(f"User not found with email: {email}")
        return None

        # Check the plain text password against the hashed password
    if not await user_obj.verify_password(password):
        print(f"Password mismatch for email: {email}")
        return None
    return user_obj

def login(user_obj,expires=settings.session_duration):
     raw_data={
         "user_id":f"{user_obj.user_id}",
         "role":"admin",
         "exp":datetime.datetime.utcnow()+datetime.timedelta(seconds=expires)
     }
     return jwt.encode(raw_data, config.Config.JWT_SECRET, algorithm=config.Config.JWT_ALGORITHM)

def verify_user_id(token):
    data={}
    try:
        data=jwt.decode(token,settings.JWT_SECRET,algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError as e:
        print(e,"logout user")
    except:
        pass
    if 'user_id' not in data:
        return None
    return data



async def get_current_user( authorization: str = Header(None), session: AsyncSession = Depends(get_session)):
    """ Using token to fetch user details from the database before granting"""
    if not authorization:
        raise HTTPException(status_code=401, detail={"status":"Error","Error":"Missing Authorization header"})

    token = authorization.split("Bearer ")[-1]  # Extract token from "Bearer <TOKEN>"
    user_data = verify_user_id(token)

    if not user_data or "user_id" not in user_data:
        raise HTTPException(status_code=401, detail={"status":"Error","Error":"Invalid or expired token"})

    user_id = user_data["user_id"]
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail={"status":"Error","Error":"User not found"}  )
    return user


