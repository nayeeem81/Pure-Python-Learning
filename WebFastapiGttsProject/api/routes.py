# api/routes.py
from fastapi import APIRouter

# Import the actual router objects from your subfiles
from api.agent import agent_router
from api.studio import studio_router
from api.frequency import frequency_router
from api.process import process_router
from api.routerwords import router_words

# The Master Router instance mounted by main.py
api_router = APIRouter()

# 💡 FIX: Mount routers directly since subfiles already define their own prefixes
api_router.include_router(process_router) 
api_router.include_router(agent_router)
api_router.include_router(studio_router)
api_router.include_router(frequency_router)
api_router.include_router(router_words)
