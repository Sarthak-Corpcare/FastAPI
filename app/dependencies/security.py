from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt, ExpiredSignatureError
from config import Settings
import uuid

settings = Settings()

def create_access_token(user_data: dict, refresh=False, expiry=None):
    if expiry is None:
        expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY) if not refresh else timedelta(
            days=settings.REFRESH_TOKEN_EXPIRY)
    raw_data = {
        "user": user_data,
        "exp": datetime.utcnow() + expiry,
        "jti": str(uuid.uuid4()),  # for revocation
        "refresh": refresh,
    }
    return jwt.encode(raw_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str):
    #  verifying and decode jwt token
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


