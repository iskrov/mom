"""FastAPI entrypoint for RemixRadar MVP."""

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
for _mod in (
    "scripts.platforms.chartmetric",
    "scripts.platforms.soundcloud",
    "scripts.pipeline",
    "server.routes.search",
):
    logging.getLogger(_mod).setLevel(logging.DEBUG)

from server.routes.meta import router as meta_router
from server.routes.search import router as search_router
from server.routes.tracks import router as tracks_router

app = FastAPI(title="RemixRadar API", version="0.1.0")

# In local dev the Vite proxy handles routing, so CORS is only needed for
# direct browser→backend calls (e.g. when testing the production build locally).
_extra_origins = [o for o in os.getenv("EXTRA_ALLOWED_ORIGINS", "").split(",") if o]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:8000",
        *_extra_origins,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(tracks_router)
app.include_router(meta_router)


@app.get("/health")
def healthcheck():
    """Simple healthcheck."""
    return {"ok": True}


# Serve the built React app when frontend/dist exists (production / local prod test).
_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if _DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        return FileResponse(_DIST / "index.html")
