# =====================================================================
# FORCE ENVIRONMENT OVERRIDES AT THE ABSOLUTE TOP OF MAIN.PY
# =====================================================================
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager 

# 1. Path Fix: Dynamically add the current folder workspace to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. Configure FFmpeg Environment path strings immediately
ffmpeg_path = r"C:\ffmpeg\bin"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]

# 3. Force early configuration initialization on Pydub before ANY internal modules load it
try:
    import pydub
    pydub.AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
    pydub.AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")
except ImportError:
    pass

# =====================================================================
# CORE APPLICATION IMPORTS (Cleaned up duplicate router references)
# =====================================================================
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text  
from sqlalchemy.ext.asyncio import create_async_engine  
from sqlmodel import SQLModel  

# Now it is completely safe to load your custom app modules
from routers.api_routes import api_router
from routers.view_routes import view_router
from config import config  
from data.database import engine
from data.model import Sentence, Word, SentenceHistory, WordHistory

# =====================================================================
# LIFECYCLE MANAGEMENT & ROUTING REGISTRATION
# =====================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    admin_url = f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/postgres"
    temp_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    
    async with temp_engine.connect() as conn:
        query = text(f"SELECT 1 FROM pg_database WHERE datname='{config.DB_NAME}'")
        result = await conn.execute(query)
        if not result.scalar():
            await conn.execute(text(f"CREATE DATABASE {config.DB_NAME}"))
            print(f"Database '{config.DB_NAME}' verified and initialized successfully.")
            
    await temp_engine.dispose()

    print("Verifying structural tables exist inside PostgreSQL...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Tables sync complete.")
    
    yield
    
    print("Shutting down application... disposing connections.")
    await engine.dispose()

app = FastAPI(title="Modern Audio Studio Backend", lifespan=lifespan)

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated") 

os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(os.path.abspath("./static"), exist_ok=True)

app.mount("/project", StaticFiles(directory="project"), name="project")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(view_router)  
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
