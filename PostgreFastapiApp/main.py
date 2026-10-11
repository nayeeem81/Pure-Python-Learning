# main.py
import threading
import time
import uvicorn
from fastapi import FastAPI
from config import config

from api.endpoints import router as agent_router  
# 1. Import your API routes
from ui.canvas_ui import AgentDesktopUI

app = FastAPI()

# 2. Register all endpoints from your subfolder
app.include_router(agent_router)

def start_fastapi_server():
    """Runs the background FastAPI daemon process."""
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT, log_level="warning")

if __name__ == "__main__":
    # Start the local FastAPI service in the background
    api_thread = threading.Thread(target=start_fastapi_server, daemon=True)
    api_thread.start()

    # Allow the internal server port to bind cleanly
    time.sleep(0.4) 

    # Launch your clean Desktop interface module
    desktop_app = AgentDesktopUI()
    desktop_app.run()
