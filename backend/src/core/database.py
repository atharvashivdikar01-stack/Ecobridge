from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import settings
engine=create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
SessionLocal=async_sessionmaker(engine,class_=AsyncSession,expire_on_commit=False)
async def get_db():
    async with SessionLocal() as session:
        yield session
async def get_async_db():
    async for db in get_db(): yield db
