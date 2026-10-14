from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask
import uvicorn

# Import your route systems from both frameworks
from api.agent import agent_router
from web.views import flask_views

# ==========================================
# 1. SETUP & CONFIGURE FLASK
# ==========================================

# In runserver.py
flask_app = Flask(__name__, template_folder="web/templates")

# Register the Flask view file (Blueprint)
flask_app.register_blueprint(flask_views)


# ==========================================
# 2. SETUP FASTAPI CONTAINER & INCLUDE ROUTER
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Main system starting up...")
    yield

api = FastAPI(lifespan=lifespan)

# Accommodate the FastAPI router perfectly:
api.include_router(agent_router)


# ==========================================
# 3. MOUNT & RUN EVERYTHING
# ==========================================
# Bridge Flask into the core server root
api.mount("/", WSGIMiddleware(flask_app))
if __name__ == "__main__":
    import uvicorn
    # Make sure the string matches your file_name:variable_name
    # If your file is named runserver.py and your FastAPI instance is named api:
    uvicorn.run("runserver:api", host="127.0.0.1", port=5001, reload=True)
