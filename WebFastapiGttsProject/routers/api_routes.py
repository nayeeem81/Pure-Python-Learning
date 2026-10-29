# routers/api_routes.py
from fastapi import APIRouter

# Updated explicit root directory absolute import targets
from api.agent import agent_router
from api.studio import studio_router
from api.frequency import frequency_router
from api.process import process_router
from api.routerwords import router_words
from api.texteditor import router_texteditor
from api.slideshow import slideshow_router
from api.imagetensor import router_imagetensor

api_router = APIRouter()

api_router.include_router(process_router) 
api_router.include_router(agent_router)
api_router.include_router(studio_router)
api_router.include_router(frequency_router)
api_router.include_router(router_words)
api_router.include_router(router_texteditor)
api_router.include_router(slideshow_router)
api_router.include_router(router_imagetensor)
