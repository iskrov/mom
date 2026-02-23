"""FastAPI entrypoint for RemixRadar MVP."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes.meta import router as meta_router
from server.routes.search import router as search_router
from server.routes.tracks import router as tracks_router

app = FastAPI(title="RemixRadar API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(tracks_router)
app.include_router(meta_router)


@app.get("/health")
def healthcheck():
    """Simple healthcheck for local dev."""
    return {"ok": True}
