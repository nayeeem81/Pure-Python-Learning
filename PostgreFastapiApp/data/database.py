# data/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import config

# Create Async Engine for PostgreSQL
engine = create_async_engine(config.DATABASE_URL, echo=True)

# Session factory for creating database links
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Base class that our models inherit from
class Base(DeclarativeBase):
    pass

# Dependency injection generator for FastAPI endpoints
async def get_db():
    async with async_session() as session:
        yield session
        await session.commit()

