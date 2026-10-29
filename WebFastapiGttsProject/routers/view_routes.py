# routers/view_routes.py
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

view_router = APIRouter(tags=["UI View Views"])
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
DEFAULT_IMAGE = BASE_DIR / "static" / "sample.png" 

@view_router.get("/", response_class=HTMLResponse)
def render_home_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"page_title": "Welcome | Dsp Engine"}
    )

@view_router.get("/audio-studio", response_class=HTMLResponse)
def render_studio_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="studio.html", 
        context={"page_title": "Gtts | Speak"}
    )

@view_router.get("/word-editor", response_class=HTMLResponse)
def render_editor_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="editor.html", 
        context={"page_title": "Workspace | Editor"}
    )

@view_router.get("/about", response_class=HTMLResponse)
def render_about_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="about.html", 
        context={"page_title": "About | Contact"}
    )

@view_router.get("/text-editor", response_class=HTMLResponse)
def render_texteditor_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="texteditor.html", 
        context={"page_title": "Text - DSP"}
    )

@view_router.get("/slideshow", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="slideshow.html", 
        context={"page_title": "Image slideshow"}
    )

@view_router.get("/editimage", response_class=HTMLResponse)
def edit_image(request: Request):
    """Serves the Image Editor interface template safely via FastAPI."""
    return templates.TemplateResponse(
        request=request, 
        name="editimage.html", 
        context={"page_title": "Edit Image"}
    )
