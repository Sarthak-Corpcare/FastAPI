from datetime import datetime
import logging
from elasticsearch import Elasticsearch
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Depends, status, HTTPException, Body, Header
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
import time
from app.db import init_db , get_session
from app.routes.auth_routes import auth_router
from app.dependencies import auth
from app.dependencies.auth import verify_user_id
from app.models.users_model import User
from app.routes.channels_routes import channel_router
from app.routes.comments_routes import comment_router
from app.routes.likes_routes import like_router
from app.routes.subscriptions_routes import subscription_router
from app.schemas.users_schema import UserLogin, UserSignup
from app.routes.videos_routes import router
from config import Settings
from fastapi_limiter import FastAPILimiter
from starlette.requests import Request
import aioredis
from app.test_logging import setup_logging
from prometheus_fastapi_instrumentator import Instrumentator

# app.add_middleware(AuthenticationMiddleware,backend=JWTCookieBackend())
app = FastAPI(title="Video Membership App")

logger = setup_logging()

REQUEST_COUNT = Counter("request_count", "Total number of requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Latency of requests", ["endpoint"])

Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def log_requests(request: Request, call_next):

    response = await call_next(request)


    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host,
        "status_code": response.status_code,
    }
    logger.info(f"Request: {log_entry}")  # Log to Loki


    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()

    return response
    
# Prometheus Metrics
@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


# using elk stack
# es = Elasticsearch("http://localhost:9200")
#
# if es.ping():
#     print("Elasticsearch is connected!")
# else:
#     print("Elasticsearch is NOT connected!")
#
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     log_entry = {
#         "timestamp": datetime.utcnow().isoformat(),
#         "method": request.method,
#         "url": str(request.url),
#         "client": request.client.host
#     }
#     logger.info(f"Request: {log_entry}")  # log request to file
#     # forwarding logs to Elasticsearch
#     response = await call_next(request)
#     return response

app.include_router(router)
app.include_router(auth_router)
app.include_router(channel_router)
app.include_router(comment_router)
app.include_router(like_router)
app.include_router(subscription_router)

settings = Settings()

@app.on_event("startup")
async def on_startup():
    print("Starting the app...")
    await init_db()
    redis_client = redis.from_url("redis://localhost", decode_responses=True)
    await FastAPILimiter.init(redis_client)
    # redis = await aioredis.from_url("redis://localhost", decode_responses=True)
    # await FastAPILimiter.init(redis)



Users=[
    {
    "email":"sanjay@gmail.com",
    "password":"#sanjay@1234",
},
    {
    "email":"suresh@gmail.com",
    "password":"#suresh@1234",
},
]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"status": "Error ","data":"nill","msg": err["msg"]} for err in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})

user_service=User()
@app.get("/users")
async def user_list_views(session:Session=Depends(get_session)):
    print("0")
    query=select(User).order_by(User.created_at)
    print("1")
    result=await session.execute(query)
    print("2")
    users=result.scalars().all()
    print(users)
    return users

@app.post("/users", response_model=User)
async def create_users(request:Request,session:AsyncSession=Depends(get_session)):
    body=await request.json()
    email=body.get("email")
    password=body.get("password")
    new_user=await User.create_user(email, password, session)
    return new_user

@app.post("/signup")
async def signup_user(data:UserSignup,session:Session=Depends(get_session)):

    query = select(User).filter(User.email == data.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()  # Returns None if not found
    if user:
        raise HTTPException(status_code=400, detail={"status":"Error","Error":"User already exists"})
    new_user=await user_service.create_user(email=data.email,password=data.password.get_secret_value(),session=session)
    return {
        "status": "Success",
        "data": {
            "user_id": str(new_user.user_id),
            "email": new_user.email,
            "created_at": str(new_user.created_at),
            "updated_at": str(new_user.updated_at),
        },
        "error": "Null"
    }


# previous login route

@app.post("/login")
async def login_user( data:UserLogin,session:AsyncSession=Depends(get_session)):
    email = data.email
    password=data.password
    password = data.password.get_secret_value()
    user_obj = await auth.authenticate(email, password, session)
    if user_obj is None:
        raise HTTPException(status_code=400, detail={"status":"Error","Error":"Incorrect Credentials, Please Try again"})
    token = auth.login(user_obj)
    return {"status":"Success","session_id":  token, "error":"Null"}


@app.post("/login_without_pydantic")
async def login_user(request: Request, email: str = Body(...), password:str = Body(...), db:AsyncSession=Depends(get_session)):
    body = await request.json()

    email = body.get("email", email)
    password = body.get("password", password)

    stmt = select(User).where(User.email==email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"status":"Error","Error":"User not found"})
    if user.verify_password(password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"status":"Error","Error":"Password didn't match"})

    return {"email":user.email,"password":user.password}


@app.get("/verify")
async def protected_route(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    token = authorization.split(" ")[1]  # Extracting the token
    user_data = verify_user_id(token)  # Verify token

    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token")

    return {"message": "Access granted", "user_data": user_data}















