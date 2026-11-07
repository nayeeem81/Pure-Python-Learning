# main.py
import os
import sys
from contextlib import asynccontextmanager 
from pathlib import Path

# ==========================================================================
# 1. ENVIRONMENT CONFIGURATION & PATH ANCHORS
# ==========================================================================
# Dynamically add the current folder workspace to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configure FFmpeg Environment path strings immediately
ffmpeg_path = r"C:\ffmpeg\bin"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]

# Force early configuration initialization on Pydub before internal modules load
try:
    import pydub
    pydub.AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
    pydub.AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")
except ImportError:
    pass


# ==========================================================================
# 2. FRAMEWORK & APP MODULE IMPORTS
# ==========================================================================
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text  
from sqlalchemy.ext.asyncio import create_async_engine  
from sqlmodel import SQLModel  

# Core application dependencies
from routers.api_routes import api_router
from routers.view_routes import view_router
from config import config  
from data.database import engine
# Keep structural model types anchored for database synchronization loops
from data.model import Sentence, Word, SentenceHistory, WordHistory, Story, Chapter, AudioChapter  


# ==========================================================================
# 3. D: DRIVE STORAGE CONTEXT REGISTRATION
# ==========================================================================
STORAGE_ROOT = "D:\\StudioStorage"
GENERATED_DIR = os.path.normpath(os.path.join(STORAGE_ROOT, "generated"))

# Initialize storage folders right away on runtime boot configuration
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(os.path.abspath("./static"), exist_ok=True)


# ==========================================================================
# 4. LIFECYCLE MANAGEMENT (LIFESPAN PROVISIONS)
# ==========================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database exists dynamically before applying migration tables
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


# ==========================================================================
# 5. APPLICATION INITIALIZATION & ROUTING MAPS
# ==========================================================================
app = FastAPI(title="Modern Audio Studio Backend", lifespan=lifespan)

# 🛠️ FIXED: Mount the D: drive folder onto the path alias /project/generated
# This enables the UI grid to load asset URLs like /project/generated/sentence_1.mp3
app.mount("/project/generated", StaticFiles(directory=GENERATED_DIR), name="d-drive-media")

# Framework web script dependency configurations
app.mount("/static", StaticFiles(directory="static"), name="static")

# Core Router Blocks
app.include_router(view_router)  
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
