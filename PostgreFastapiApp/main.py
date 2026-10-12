# main.py
import threading
import time
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from config import config
from data.database import engine, Base
from api.endpoints import router as agent_router
from ui.canvas_ui import AgentDesktopUI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Micro-handshake connection setup to provision database shell if missing
    admin_url = f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/postgres"
    temp_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    
    async with temp_engine.connect() as conn:
        # Check if the database catalog target exists
        query = text(f"SELECT 1 FROM pg_database WHERE datname='{config.DB_NAME}'")
        result = await conn.execute(query)
        if not result.scalar():
            await conn.execute(text(f"CREATE DATABASE {config.DB_NAME}"))
            
    await temp_engine.dispose()

    # 2. Proceed with primary mapping initialization loops
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(agent_router)

def start_fastapi_server():
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT, log_level="warning")

if __name__ == "__main__":
    api_thread = threading.Thread(target=start_fastapi_server, daemon=True)
    api_thread.start()

    time.sleep(0.4) 

    desktop_app = AgentDesktopUI()
    desktop_app.run()
