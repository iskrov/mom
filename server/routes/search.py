"""Search routes for RemixRadar MVP API."""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from scripts.models import compute_demand_score
from scripts.catalog import parse_catalog_file
from scripts.pipeline import (
    analyze_track_object,
    make_clients,
    search_song_remixes,
)
from server.schemas import AnalyzeUrlRequest, ArtistSearchRequest, SongSearchRequest

router = APIRouter(prefix="/api", tags=["search"])
_NUMERIC_PREFIX_RE = re.compile(r"^\d{4,}\s+")
_LABEL_SPLIT_RE = re.compile(r"\s*[|;/]\s*")
_COUNTRY_SUFFIX_RE = re.compile(r"\b[A-Z]{2,3}$")


def _score_label_candidate(label: str) -> int:
    raw = (label or "").strip()
    if not raw:
        return -10_000

    score = 0
    lowered = raw.lower()

    if _NUMERIC_PREFIX_RE.match(raw):
        score -= 80
    if lowered in {"unknown", "n/a", "none"}:
        score -= 50
    if any(token in lowered for token in ("records", "recordings", "music", "entertainment", "bros")):
        score += 20
    if _COUNTRY_SUFFIX_RE.search(raw) and len(raw.split()) <= 4:
        score -= 10

    score += min(len(raw), 40) // 8
    return score


def _pick_track_label(original_track: dict) -> str:
    candidates: list[str] = []

    album_record_label = original_track.get("album_record_label")
    if isinstance(album_record_label, str) and album_record_label.strip():
        candidates.append(album_record_label.strip())

    direct = original_track.get("track_record_label")
    if isinstance(direct, str) and direct.strip():
        candidates.append(direct.strip())

    album_label = original_track.get("album_label")
    if isinstance(album_label, list):
        for item in album_label:
            text = str(item).strip()
            if text:
                candidates.append(text)
    elif isinstance(album_label, str):
        text = album_label.strip()
        if text:
            candidates.extend([part for part in _LABEL_SPLIT_RE.split(text) if part])

    if not candidates:
        return ""

    return max(candidates, key=_score_label_candidate).strip()


def _pick_release_date(original_track: dict) -> str:
    value = (original_track.get("release_date") or "").strip()
    return value


def _pick_songwriters(original_track: dict) -> list[str]:
    raw = original_track.get("songwriters")
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return []


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
    original_track = report.get("original_track") or {}
    remix_career = remix_artist.get("career") or {}
    original_career = original_artist.get("career") or {}

    track_label = _pick_track_label(original_track)
    track_release_date = _pick_release_date(original_track)
    track_songwriters = _pick_songwriters(original_track)
    artist_label = (original_artist.get("record_label") or "").strip()
    if track_label:
        record_label = track_label
    elif original_track:
        # Do not regress to artist-level label when we already have a track match but no reliable track label.
        record_label = "Unknown"
    else:
        record_label = artist_label

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
            "tiktok_followers": remix_artist.get("tiktok_followers"),
            "career_stage": remix_career.get("stage"),
            "momentum": remix_career.get("momentum"),
            "geo_cities": remix_artist.get("geo_cities") or [],
        },
        "original_artist_enriched": {
            "name": original_artist.get("name"),
            "sp_monthly_listeners": original_artist.get("sp_monthly_listeners"),
            "career_stage": original_career.get("stage"),
            "record_label": record_label,
            "geo_cities": original_artist.get("geo_cities") or [],
        },
        "original_track_enriched": {
            "cm_track_id": original_track.get("cm_track_id"),
            "isrc": original_track.get("isrc"),
            "release_date": track_release_date,
            "songwriters": track_songwriters,
            "match_confidence": original_track.get("match_confidence"),
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
            report = analyze_track_object(track, clients, original_isrc_override=payload.isrc_override)
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
async def search_catalog(file: UploadFile = File(...), limit_remixes: int = Form(5), min_plays: int = Form(0)):
    """
    Catalog workflow — SSE stream of enriched remix results per song.

    Emits:
      status  {"message": "catalog_loaded", "count": N}
      status  {"message": "processing_song", "song": str, "index": N, "total": N}
      track   {"track": TrackResult, "song": str, "song_index": N}
      complete {"count": N, "results": [...]}
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".csv", ".xml"}:
        raise HTTPException(status_code=400, detail="Catalog file must be .csv or .xml")

    safe_limit = max(1, min(int(limit_remixes or 5), 20))
    safe_min_plays = max(0, int(min_plays or 0))
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded catalog file is empty")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        temp_path = tmp.name

    def stream():
        try:
            records = parse_catalog_file(temp_path)

            # Deduplicate by ISRC so the same song isn't processed twice.
            seen_isrcs: set[str] = set()
            deduped = []
            for r in records:
                isrc = r.get("isrc")
                if isrc:
                    if isrc in seen_isrcs:
                        continue
                    seen_isrcs.add(isrc)
                deduped.append(r)

            songs = [r for r in deduped if r.get("title")]
            yield _sse_event("status", {"message": "catalog_loaded", "count": len(songs)})

            clients = make_clients()
            all_items: list[dict] = []

            for idx, record in enumerate(songs, start=1):
                title = record["title"]
                artist = record.get("artist")
                yield _sse_event("status", {
                    "message": "processing_song",
                    "song": title,
                    "index": idx,
                    "total": len(songs),
                })

                reports = search_song_remixes(
                    song_name=title, artist_name=artist,
                    limit=safe_limit, clients=clients,
                )
                if safe_min_plays > 0:
                    reports = [
                        r for r in reports
                        if (r.get("sc_metrics") or {}).get("plays", 0) >= safe_min_plays
                    ]

                for report in reports:
                    item = _summarize_report(report)
                    all_items.append(item)
                    yield _sse_event("track", {"track": item, "song": title, "song_index": idx})

            dedup_map = {item["track_id"]: item for item in all_items}
            ranked = sorted(
                dedup_map.values(),
                key=lambda row: (row.get("opportunity_score") or {}).get("overall", 0),
                reverse=True,
            )
            yield _sse_event("complete", {"count": len(ranked), "results": list(ranked)})
        finally:
            path_obj = Path(temp_path)
            if path_obj.exists():
                path_obj.unlink()

    return StreamingResponse(stream(), media_type="text/event-stream")
