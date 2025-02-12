from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session
from app.services.token_service import is_jti_blocked
from app.dependencies.security import verify_token


class AccessTokenBearer(HTTPBearer):
    # Dependency for verifying access tokens
    async def __call__(self, request: Request,session: AsyncSession = Depends(get_session)):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        token = credentials.credentials

        token_data = verify_token(token)
        if await is_jti_blocked(token_data["jti"],session=session):
            raise HTTPException(status_code=401, detail="Token revoked")
        return token_data

class RefreshTokenBearer(HTTPBearer):
    # Dependency for verifying refresh tokens
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        token = credentials.credentials
        token_data = verify_token(token)

        if not token_data.get("refresh"):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        return token_data
