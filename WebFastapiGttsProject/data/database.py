# data/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession  # 💡 Uses SQLModel's AsyncSession for .exec() compatibility
from config import config

# Create Async Engine for PostgreSQL
engine = create_async_engine(config.DATABASE_URL, echo=True)

# Session factory bound to SQLModel's AsyncSession implementation
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Dependency injection generator for FastAPI endpoints
async def get_db():
    async with async_session() as session:
        yield session
        await session.commit()
