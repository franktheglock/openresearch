from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from .config import settings
from .routers.research import router as research_router
from .routers.settings import router as settings_router


def create_app() -> FastAPI:
    app = FastAPI(title="OpenResearch API", version="0.1.0")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(research_router, prefix="/api")
    app.include_router(settings_router, prefix="/api")

    # Static files for frontend
    frontend_path = Path(__file__).parent.parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
        
        @app.get("/")
        async def root():
            return RedirectResponse(url="/static/index.html")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
