"""Search routes for RemixRadar MVP API."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from scripts.models import compute_demand_score
from scripts.pipeline import (
    analyze_track_object,
    make_clients,
    process_catalog,
)
from server.schemas import AnalyzeUrlRequest, ArtistSearchRequest, SongSearchRequest

router = APIRouter(prefix="/api", tags=["search"])


def _classify_heat_trend(sc_metrics: dict) -> str:
    """Classify trend using normalized daily velocity."""
    days_live = max(int(sc_metrics.get("days_live") or 1), 1)
    velocity = float(sc_metrics.get("daily_velocity") or 0.0)
    normalized = velocity / max(days_live**0.25, 1.0)
    if normalized >= 1200:
        return "rising"
    if normalized <= 250:
        return "declining"
    return "steady"


def _summarize_report(report: dict) -> dict:
    """Convert raw pipeline report into API-friendly shape."""
    parsed = report.get("parsed_title", {})
    sc_track = report.get("sc_track", {})
    sc_user = sc_track.get("user", {})
    sc_metrics = report.get("sc_metrics", {})
    opportunity_raw = report.get("opportunity_score", {})

    heat = round((compute_demand_score(sc_metrics) / 10.0), 1)
    opp = {
        "overall": round((opportunity_raw.get("overall", 0.0) / 10.0), 1),
        "label": opportunity_raw.get("label", "WEAK"),
        "demand": round((opportunity_raw.get("demand", 0.0) / 10.0), 1),
        "conversion": round((opportunity_raw.get("conversion", 0.0) / 10.0), 1),
        "momentum": round((opportunity_raw.get("momentum", 0.0) / 10.0), 1),
    }

    remix_artist = report.get("remix_artist") or {}
    original_artist = report.get("original_artist") or {}
    remix_career = remix_artist.get("career") or {}
    original_career = original_artist.get("career") or {}

    return {
        "track_id": report.get("track_id"),
        "title": report.get("track_title"),
        "original_song": parsed.get("original_song"),
        "permalink_url": report.get("sc_url"),
        "genre": report.get("track_genre"),
        "created_at": sc_track.get("created_at"),
        "remix_artist": parsed.get("remix_artist") or sc_user.get("username"),
        "original_artist": parsed.get("original_artist"),
        "sc_user": {
            "username": sc_user.get("username"),
            "followers_count": sc_user.get("followers_count") or 0,
            "track_count": sc_user.get("track_count") or 0,
            "avatar_url": sc_user.get("avatar_url"),
        },
        "plays": sc_metrics.get("plays", 0),
        "likes": sc_metrics.get("likes", 0),
        "reposts": sc_metrics.get("reposts", 0),
        "comments": sc_metrics.get("comments", 0),
        "engagement_rate": sc_metrics.get("engagement_rate", 0),
        "daily_velocity": sc_metrics.get("daily_velocity", 0),
        "days_live": sc_metrics.get("days_live", 0),
        "heat_score": heat,
        "heat_trend": _classify_heat_trend(sc_metrics),
        "opportunity_score": opp,
        "remix_artist_enriched": {
            "name": remix_artist.get("name"),
            "sp_followers": remix_artist.get("sp_followers"),
            "sp_monthly_listeners": remix_artist.get("sp_monthly_listeners"),
            "career_stage": remix_career.get("stage"),
            "momentum": remix_career.get("momentum"),
            "geo_cities": remix_artist.get("geo_cities") or [],
        },
        "original_artist_enriched": {
            "name": original_artist.get("name"),
            "sp_monthly_listeners": original_artist.get("sp_monthly_listeners"),
            "career_stage": original_career.get("stage"),
            "geo_cities": original_artist.get("geo_cities") or [],
        },
        "revenue": report.get("revenue", {}),
        "viability": report.get("viability", {}),
    }


def _sse_event(event_type: str, payload: dict) -> str:
    """Encode one SSE event block."""
    return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"


@router.post("/search/artist")
def search_artist(payload: ArtistSearchRequest):
    """SSE stream of fully enriched artist-remix results."""
    if not payload.enrich_chartmetric:
        raise HTTPException(status_code=400, detail="Chartmetric enrichment must stay enabled for MVP.")

    clients = make_clients()
    sc = clients["sc"]

    def stream():
        yield _sse_event("status", {"message": "search_started", "artist": payload.artist_name})
        seed_tracks = sc.search_tracks(query=f"{payload.artist_name} remix", limit=payload.tracks_to_fetch)
        yield _sse_event("status", {"message": "tracks_found", "count": len(seed_tracks)})

        reports: list[dict] = []
        for idx, track in enumerate(seed_tracks, start=1):
            report = analyze_track_object(track, clients)
            item = _summarize_report(report)
            reports.append(item)
            yield _sse_event("track", {"index": idx, "total": len(seed_tracks), "track": item})

        reverse = payload.sort_desc
        sort_key = payload.sort_by if payload.sort_by in {"heat_score", "plays", "likes", "daily_velocity"} else "heat_score"
        reports.sort(key=lambda row: row.get(sort_key) or 0, reverse=reverse)
        yield _sse_event("complete", {"count": len(reports), "results": reports})

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/search/song")
def search_song(payload: SongSearchRequest):
    """SSE stream of fully enriched song-remix results."""
    if not payload.enrich_chartmetric:
        raise HTTPException(status_code=400, detail="Chartmetric enrichment must stay enabled for MVP.")

    clients = make_clients()
    sc = clients["sc"]

    def stream():
        yield _sse_event("status", {"message": "search_started", "song": payload.song_name})
        tracks = sc.search_remixes(payload.song_name, artist=payload.artist_name, limit=payload.tracks_to_fetch)
        yield _sse_event("status", {"message": "tracks_found", "count": len(tracks)})

        reports: list[dict] = []
        for idx, track in enumerate(tracks, start=1):
            report = analyze_track_object(track, clients)
            item = _summarize_report(report)
            reports.append(item)
            yield _sse_event("track", {"index": idx, "total": len(tracks), "track": item})

        reports.sort(key=lambda row: row.get("heat_score") or 0, reverse=True)
        yield _sse_event("complete", {"count": len(reports), "results": reports})

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/analyze/url")
def analyze_url(payload: AnalyzeUrlRequest):
    """Analyze one SoundCloud URL and return one enriched result."""
    clients = make_clients()
    sc_track = clients["sc"].resolve(payload.sc_url)
    report = analyze_track_object(sc_track, clients)
    return _summarize_report(report)


@router.post("/search/catalog")
async def search_catalog(file: UploadFile = File(...), limit_remixes: int = Form(5)):
    """
    Catalog workflow entrypoint.

    Accepts a CSV/XML upload and returns fully enriched ranked results.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".csv", ".xml"}:
        raise HTTPException(status_code=400, detail="Catalog file must be .csv or .xml")

    safe_limit = max(1, min(int(limit_remixes or 5), 20))
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded catalog file is empty")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            temp_path = tmp.name

        clients = make_clients()
        reports = process_catalog(temp_path, limit_remixes=safe_limit, clients=clients)
        summarized = [_summarize_report(report) for report in reports]
        return {"count": len(summarized), "results": summarized}
    finally:
        if temp_path:
            path_obj = Path(temp_path)
            if path_obj.exists():
                path_obj.unlink()
