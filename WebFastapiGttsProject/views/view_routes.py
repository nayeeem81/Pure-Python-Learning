from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

view_router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# 1. Route to render the Home Page UI
@view_router.get("/", response_class=HTMLResponse)
def render_home_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html",  # <-- Change this from "home.html" to "index.html"
        context={"page_title": "Welcome | Audio Engine"}
    )


# 2. Existing dashboard workspace route
@view_router.get("/audio-studio", response_class=HTMLResponse)
def render_studio_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="studio.html", 
        context={"page_title": "Workspace | Audio Studio"}
    )
