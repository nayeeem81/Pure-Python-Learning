# routers/api_routes.py
from fastapi import APIRouter
# Updated explicit root directory absolute import targets
from api.gttsagent import router_gttsagent
from api.gttsanalyzer import router_gttsanalyzer
from api.gttsprocess import router_gttsprocess
from api.gttsword import router_gttsword
from api.sentence import router_sentence
from api.slideshow import router_slideshow
from api.magiclens import router_magiclens
from api.paragraph import router_paragraph

api_router = APIRouter()

api_router.include_router(router_gttsprocess)
api_router.include_router(router_gttsagent)
api_router.include_router(router_gttsanalyzer)
api_router.include_router(router_gttsword)
api_router.include_router(router_sentence)
api_router.include_router(router_slideshow)
api_router.include_router(router_magiclens)
api_router.include_router(router_paragraph)

