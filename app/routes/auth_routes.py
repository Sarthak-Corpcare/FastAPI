from argon2 import verify_password
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_session
from app.dependencies.auth_depends import RefreshTokenBearer, AccessTokenBearer
from app.dependencies.security import create_access_token
from app.models.users_model import User
from app.test_logging import setup_logging

from app.schemas.users_schema import UserLogin

from app.services.token_service import add_jti_to_blocklist, is_jti_blocked
from config import Settings

settings = Settings()
logger=setup_logging()
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/login")
async def login_user(data: UserLogin, session: AsyncSession = Depends(get_session)):
    # Logining in user and returning access & refresh tokens

    query = select(User).where(User.email == data.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    password = data.password.get_secret_value()
    if not user or not await user.verify_password(password):
        logger.error("Invalid login attempt for email: %s", data.email)
        raise HTTPException(status_code=403, detail="Invalid Email or Password")

    access_token = create_access_token(
        user_data={"email": user.email, "user_id": str(user.user_id)}
    )

    refresh_token = create_access_token(
        user_data={"email": user.email, "user_id": str(user.user_id)},
        refresh=True,
        expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRY)
    )
    logger.info("User logged in successfully: %s", data.email)
    logger.info("Everything working and logs appearing ")
    return JSONResponse(
        content={
            "status":"Success",
            "message": "Login Successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"email": user.email, "user_id": str(user.user_id)},
            "error":"Null"
        }
    )



@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    # Generating a new access token from the refresh token.

    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(status_code=400, detail="Invalid or expired token")


@auth_router.get("/me")
async def get_current_user(user: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    if await is_jti_blocked(user["jti"], session=session):  # Pass session here
        raise HTTPException(status_code=401, detail="Token revoked")
    """Fetch current authenticated user details."""
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    """Logout by adding JWT ID (jti) to blocklist."""

    jti = token_details["jti"]
    if await is_jti_blocked(jti, session):
        raise HTTPException(status_code=401, detail="Token already revoked")
    await add_jti_to_blocklist(jti,session)
    return JSONResponse(content={"status":"Success","message": "Logged out successfully","error":"Null"})
