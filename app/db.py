from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine,SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from config import Config


# echo=True for logging
async_engine=AsyncEngine(create_engine(url=Config.DATABASE_URL,echo=True))
#create_engine is use to create sqlalchemy engine to create to database

async def init_db():
    async with async_engine.begin() as conn: # open transactional connection database
        await conn.run_sync(SQLModel.metadata.create_all) # contains matadeta about database and create all table related to it

async def get_session()->AsyncSession:
    Session=sessionmaker(bind=async_engine,class_=AsyncSession,expire_on_commit=False)
    async with Session() as session:
        yield session
