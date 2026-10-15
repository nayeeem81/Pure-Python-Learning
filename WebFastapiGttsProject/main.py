# Orchestrator: mounts assets, includes routers
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes import api_router
from views.view_routes import view_router

app = FastAPI(title="Modern Audio Studio Backend")

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated") 

# Mount visual layer assets
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/project", StaticFiles(directory="project"), name="project")

app.include_router(view_router)                 # Renders the HTML templates
app.include_router(api_router, prefix="/api")   # Executes computational tasks

# Add this to the very bottom of main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
