from fastapi import APIRouter
# Absolute imports from your internal files
from api.agent import agent_router
from api.studio import studio_router
from api.frequency import frequency_router

# The Master Router instance
api_router = APIRouter()

# Combine sub-modules into the master coordinator
api_router.include_router(agent_router)
api_router.include_router(studio_router)
api_router.include_router(frequency_router)
