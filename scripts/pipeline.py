#!/usr/bin/env python3
"""
Remix Radar pipeline orchestrator and reusable workflow service layer.

This module now exposes reusable analysis functions suitable for both:
- CLI workflows (current hackathon usage)
- future FastAPI endpoints (planned)
"""

import argparse
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

logger = logging.getLogger(__name__)

from scripts.catalog import parse_catalog_file
from scripts.config import cfg
from scripts.models import (
    assess_viability,
    build_opportunity_score,
    parse_remix_title,
    project_revenue,
)
from scripts.platforms import ChartmetricClient, LuminateClient, SoundCloudClient
from scripts.reporting import format_summary_table, format_track_report


DEFAULT_URL = "https://soundcloud.com/revelriesmusic/blinding_lights"

_NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]+")
_SPACE_RE = re.compile(r"\s+")
# Splits "The Chainsmokers & Coldplay" or "Calvin Harris feat. Rihanna" into individual names.
# Requires whitespace on both sides so "R&B" or "Guns N' Roses" are not split.
_COLLAB_RE = re.compile(r"\s+(?:&|feat\.?|ft\.?)\s+", re.IGNORECASE)
_REMIX_MARKERS = {
    "remix",
    "edit",
    "bootleg",
    "mashup",
    "flip",
    "rework",
    "cover",
    "acoustic",
    "live",
    "nightcore",
    "slowed",
    "sped",
}


def _extract_release_date(track_obj):
    release_date = (track_obj.get("release_date") or "").strip()
    if release_date:
        return release_date

    release_dates = track_obj.get("release_dates")
    if isinstance(release_dates, str):
        return release_dates.strip() or None
    if isinstance(release_dates, list):
        cleaned = sorted([str(d).strip() for d in release_dates if str(d).strip()])
        if cleaned:
            return cleaned[0]
    return None


def _extract_songwriters(track_obj):
    names = []
    seen = set()

    def _is_valid_name(text):
        # Drop obvious non-name payload fragments (pure numbers, id blobs, etc.).
        if not text:
            return False
        compact = text.replace(" ", "")
        if compact.isdigit():
            return False
        if len(text) < 3:
            return False
        return True

    def _add(name):
        raw = str(name or "").strip()
        if not raw:
            return
        # Chartmetric may return a comma-joined songwriter blob in a single string.
        parts = [part.strip() for part in raw.split(",")]
        for text in parts:
            if not _is_valid_name(text):
                continue
            key = text.lower()
            if key not in seen:
                seen.add(key)
                names.append(text)

    for key in ("songwriters", "cm_songwriters"):
        raw = track_obj.get(key)
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    _add(item.get("name") or item.get("songwriter_name"))
                else:
                    _add(item)

    _add(track_obj.get("composer_name"))
    return names


def resolve_track_by_isrc(cm, isrc):
    """Resolve canonical Chartmetric track metadata by ISRC."""
    clean_isrc = (isrc or "").strip().upper()
    if not clean_isrc:
        return None

    if clean_isrc in cm._track_isrc_cache:
        logger.debug("resolve_track_by_isrc: cache hit for %s", clean_isrc)
        return cm._track_isrc_cache[clean_isrc]

    try:
        ids_obj = cm.get_track_ids_by_isrc(clean_isrc) or {}
        if isinstance(ids_obj, list):
            ids_row = ids_obj[0] if ids_obj else {}
        elif isinstance(ids_obj, dict):
            ids_row = ids_obj
        else:
            ids_row = {}
        cm_ids = ids_row.get("chartmetric_ids") or []
        if not cm_ids:
            cm._track_isrc_cache[clean_isrc] = None
            return None
        cm_track_id = cm_ids[0]
        full = cm.get_track(cm_track_id) or {}
    except Exception:
        cm._track_isrc_cache[clean_isrc] = None
        return None

    album_record_label = ""
    album_ids = full.get("album_ids") or []
    release_dates = full.get("release_dates") or []

    album_order: list[int] = []
    if isinstance(album_ids, list) and album_ids:
        if isinstance(release_dates, list) and len(release_dates) == len(album_ids):
            paired = sorted(zip(release_dates, album_ids), key=lambda p: str(p[0] or "9999-99-99"))
            album_order = [album_id for _, album_id in paired]
        else:
            album_order = list(album_ids)

    for album_id in album_order[:5]:
        try:
            album_meta = cm.get_album(album_id) or {}
        except Exception:
            album_meta = {}
        candidate = (album_meta.get("label") or "").strip()
        if candidate:
            album_record_label = candidate
            break

    artist_names = full.get("artist_names") or []
    if not artist_names:
        raw_artists = full.get("artists") or []
        artist_names = [a["name"] for a in raw_artists if isinstance(a, dict) and a.get("name")]

    result = {
        "cm_track_id": cm_track_id,
        "name": full.get("name"),
        "isrc": full.get("isrc") or clean_isrc,
        "artist_names": artist_names,
        "release_date": _extract_release_date(full),
        "songwriters": _extract_songwriters(full),
        "album_label": full.get("album_label"),
        "album_record_label": album_record_label,
        "track_record_label": full.get("record_label") or full.get("label"),
        "match_confidence": 1.0,
    }
    cm._track_isrc_cache[clean_isrc] = result
    return result


def _print_banner():
    print("=" * 72)
    print("Remix Radar -- Pipeline")
    print("Measure of Music 2026 Hackathon")
    print("=" * 72)
    print("Time:  ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def _print_credentials():
    print("\nCredential Check")
    print("-" * 72)
    for name, ok in cfg.check_credentials():
        status = "OK" if ok else "MISSING"
        print(f"{name:<32} {status}")


def enrich_artist(cm, artist_name):
    """
    Reusable artist enrichment function.

    Returns a normalized dict used in scoring and reporting.
    """
    if not artist_name:
        return None
    cache_key = artist_name.lower().strip()
    if cache_key in cm._artist_cache:
        logger.debug("enrich_artist: cache hit for %r", artist_name)
        return cm._artist_cache[cache_key]
    logger.debug("enrich_artist: searching for %r", artist_name)
    t0 = time.perf_counter()
    try:
        search_result = cm.find_artist(artist_name)
    except Exception:
        logger.warning("enrich_artist: Chartmetric lookup failed for %r", artist_name, exc_info=True)
        cm._artist_cache[cache_key] = None
        return None
    if not search_result:
        logger.debug("enrich_artist: no result for %r (%.2fs)", artist_name, time.perf_counter() - t0)
        cm._artist_cache[cache_key] = None
        return None

    cm_id = search_result.get("id")
    logger.debug("enrich_artist: found cm_id=%s for %r, fetching metadata", cm_id, artist_name)
    try:
        meta = cm.get_artist(cm_id)
    except Exception:
        logger.warning("enrich_artist: get_artist failed for cm_id=%s", cm_id, exc_info=True)
        meta = {}
    career = {}
    try:
        career = cm.get_artist_career(cm_id)
    except Exception:
        career = {}
    if isinstance(career, list):
        career = career[0] if career else {}
    if not isinstance(career, dict):
        career = {}
    cities = []
    try:
        ids = cm.get_artist_platform_ids(cm_id)
        platform_ids = ids[0] if isinstance(ids, list) and ids else (ids or {})
    except Exception:
        platform_ids = {}
    cities = []

    logger.debug("enrich_artist: done %r in %.2fs", artist_name, time.perf_counter() - t0)
    result = {
        "input_name": artist_name,
        "cm_id": cm_id,
        "name": search_result.get("name") or meta.get("name"),
        "sp_followers": search_result.get("sp_followers"),
        "sp_monthly_listeners": search_result.get("sp_monthly_listeners"),
        "spotify_followers_to_listeners_ratio": search_result.get("spotify_followers_to_listeners_ratio"),
        "spotify_listeners_to_followers_ratio": search_result.get("spotify_listeners_to_followers_ratio"),
        "tiktok_followers": search_result.get("tiktok_followers"),
        "cm_artist_score": search_result.get("cm_artist_score"),
        "record_label": meta.get("record_label"),
        "genres": meta.get("genres"),
        "career": career,
        "geo_cities": cities,
        "platform_ids": platform_ids,
        "search_result": search_result,
        "metadata": meta,
    }
    cm._artist_cache[cache_key] = result
    return result


def find_original_isrc(cm, artist_name, song_name):
    """Find likely original track ISRC via Chartmetric track search."""
    if not artist_name or not song_name:
        return None
    logger.debug("find_original_isrc: %r – %r", artist_name, song_name)
    _t0 = time.perf_counter()

    def _norm(value):
        text = (value or "").lower()
        text = _NON_ALNUM_RE.sub(" ", text)
        return _SPACE_RE.sub(" ", text).strip()

    def _artist_names(obj):
        names = []
        raw_names = obj.get("artist_names")
        if isinstance(raw_names, list):
            names.extend([_norm(n) for n in raw_names if n])
        elif isinstance(raw_names, str):
            names.append(_norm(raw_names))

        raw_artists = obj.get("artists")
        if isinstance(raw_artists, list):
            for item in raw_artists:
                if isinstance(item, dict):
                    name = item.get("name")
                    if name:
                        names.append(_norm(name))
                elif isinstance(item, str):
                    names.append(_norm(item))
        elif isinstance(raw_artists, str):
            names.append(_norm(raw_artists))

        # Deduplicate while preserving order.
        deduped = []
        seen = set()
        for name in names:
            if name and name not in seen:
                seen.add(name)
                deduped.append(name)
        return deduped

    def _artist_match(target, candidates):
        if not target or not candidates:
            return False
        target_tokens = [t for t in target.split() if t]
        for cand in candidates:
            if target in cand or cand in target:
                return True
            cand_tokens = [t for t in cand.split() if t]
            overlap = len(set(target_tokens).intersection(cand_tokens))
            if overlap >= 2:
                return True
        return False

    def _score_track_candidate(candidate):
        score = 0

        target_song = _norm(song_name)
        target_artist = _norm(artist_name)
        cand_name = _norm(candidate.get("name"))
        cand_artists = _artist_names(candidate)

        if cand_name == target_song:
            score += 140
        elif target_song and target_song in cand_name:
            score += 80
        elif cand_name and target_song and any(tok in cand_name for tok in target_song.split()):
            score += 25

        artist_match = _artist_match(target_artist, cand_artists)
        if artist_match:
            score += 120
        elif target_artist and cand_artists:
            # Strong penalty if we have artist data and it doesn't match the requested original artist.
            score -= 120

        if cand_name and any(marker in cand_name.split() for marker in _REMIX_MARKERS):
            score -= 80

        if candidate.get("isrc"):
            score += 10

        return score

    query = f"{artist_name} {song_name}"
    tracks = cm.search(query, "tracks", limit=10)
    if not tracks:
        logger.debug("find_original_isrc: no tracks found for %r (%.2fs)", query, time.perf_counter() - _t0)
        return None

    scored = sorted(
        [{"track": track, "score": _score_track_candidate(track)} for track in tracks],
        key=lambda row: row["score"],
        reverse=True,
    )
    logger.debug("find_original_isrc: fetching full metadata for top %d candidates", min(5, len(scored)))
    finalists = []
    for row in scored[:5]:
        track = row["track"]
        try:
            full_track = cm.get_track(track.get("id")) or {}
        except Exception:
            full_track = {}
        merged = {**track, **full_track}
        finalists.append({"track": track, "full": full_track, "score": _score_track_candidate(merged)})

    finalists.sort(key=lambda row: row["score"], reverse=True)
    top = finalists[0]["track"]
    full = finalists[0]["full"] or {}
    top_score = int(finalists[0]["score"])
    score_gap = top_score - int(finalists[1]["score"]) if len(finalists) > 1 else top_score
    match_confidence = round(max(min((top_score + max(score_gap, 0) * 0.5) / 260.0, 1.0), 0.0), 2)

    isrc = full.get("isrc") or top.get("isrc")

    # Canonicalize by ISRC to avoid remix/regional variants from search ordering.
    canonical_full = {}
    canonical_track_id = None
    if isrc:
        try:
            ids_obj = cm.get_track_ids_by_isrc(isrc) or {}
            if isinstance(ids_obj, list):
                ids_row = ids_obj[0] if ids_obj else {}
            elif isinstance(ids_obj, dict):
                ids_row = ids_obj
            else:
                ids_row = {}
            cm_ids = ids_row.get("chartmetric_ids") or []
            if cm_ids:
                canonical_track_id = cm_ids[0]
                canonical_full = cm.get_track(canonical_track_id) or {}
        except Exception:
            canonical_full = {}

    label_source = canonical_full or full
    album_record_label = ""
    album_ids = label_source.get("album_ids") or []
    release_dates = label_source.get("release_dates") or []

    # Prioritize oldest known release to approximate the original master.
    album_order: list[int] = []
    if isinstance(album_ids, list) and album_ids:
        if isinstance(release_dates, list) and len(release_dates) == len(album_ids):
            paired = sorted(zip(release_dates, album_ids), key=lambda p: str(p[0] or "9999-99-99"))
            album_order = [album_id for _, album_id in paired]
        else:
            album_order = list(album_ids)

    for album_id in album_order[:5]:
        try:
            album_meta = cm.get_album(album_id) or {}
        except Exception:
            album_meta = {}
        candidate = (album_meta.get("label") or "").strip()
        if candidate:
            album_record_label = candidate
            break

    album_label = (
        label_source.get("album_label")
        or top.get("album_label")
    )
    track_record_label = (
        label_source.get("record_label")
        or label_source.get("label")
        or full.get("record_label")
        or full.get("label")
        or top.get("record_label")
        or top.get("label")
    )
    logger.debug("find_original_isrc: done %r – %r in %.2fs (isrc=%s)", artist_name, song_name, time.perf_counter() - _t0, isrc)
    return {
        "cm_track_id": canonical_track_id or top.get("id"),
        "name": label_source.get("name") or full.get("name") or top.get("name"),
        "isrc": isrc,
        "artist_names": label_source.get("artist_names") or full.get("artist_names") or top.get("artist_names") or [],
        "release_date": _extract_release_date(label_source),
        "songwriters": _extract_songwriters(label_source),
        "album_label": album_label,
        "album_record_label": album_record_label,
        "track_record_label": track_record_label,
        "match_confidence": match_confidence,
    }


def fetch_luminate_by_isrc(lum, isrc):
    """Try Luminate lookup (optional, fails gracefully)."""
    if not isrc:
        return None
    try:
        return lum.get_consumption_by_isrc(isrc)
    except Exception:
        return None


def normalize_sc_track(track):
    """Normalize SoundCloud track object to core fields used across workflows."""
    return {
        "id": track.get("id"),
        "title": track.get("title"),
        "genre": track.get("genre"),
        "created_at": track.get("created_at"),
        "permalink_url": track.get("permalink_url"),
        "user": track.get("user", {}),
        "raw": track,
    }


def _enrich_possibly_multi_artist(cm, artist_name):
    """
    Enrich an artist name that may contain multiple collaborators (e.g. "A & B").

    Splits on common collab separators, enriches each artist individually,
    and returns a merged dict where sp_monthly_listeners and sp_followers
    are summed across all found artists. Falls back to single-artist lookup
    if no split is needed or no collaborators are found.
    """
    if not artist_name:
        return None
    parts = [p for p in _COLLAB_RE.split(artist_name) if p.strip()]
    if len(parts) <= 1:
        return enrich_artist(cm, artist_name)

    logger.debug("enrich_artist: multi-artist split %r → %r", artist_name, parts)
    enriched = [enrich_artist(cm, p) for p in parts]
    enriched = [a for a in enriched if a]
    if not enriched:
        return None
    if len(enriched) == 1:
        return enriched[0]

    merged = dict(enriched[0])
    merged["name"] = " & ".join(a["name"] for a in enriched if a.get("name"))
    merged["sp_monthly_listeners"] = sum(a.get("sp_monthly_listeners") or 0 for a in enriched) or None
    merged["sp_followers"] = sum(a.get("sp_followers") or 0 for a in enriched) or None
    merged["tiktok_followers"] = sum(a.get("tiktok_followers") or 0 for a in enriched) or None
    logger.debug("enrich_artist: merged monthly_listeners=%s", merged["sp_monthly_listeners"])
    return merged


def analyze_track_object(sc_track, clients, original_isrc_override=None, min_plays=0):
    """
    Core reusable per-track analysis function.

    This is the API-ready service function that all workflows call.
    """
    sc = clients["sc"]
    cm = clients["cm"]
    lum = clients["lum"]

    norm_track = normalize_sc_track(sc_track)
    title = norm_track["title"] or ""
    logger.debug("analyze_track: start  %r", title)
    _t0 = time.perf_counter()

    parsed = parse_remix_title(title)
    sc_metrics = sc.compute_metrics(sc_track)

    plays = sc_metrics.get("plays", 0)
    if min_plays > 0 and plays < min_plays:
        logger.debug("analyze_track: skip  %r  plays=%d < min_plays=%d", title, plays, min_plays)
        return None
    logger.debug("analyze_track: plays=%d passed gate (min_plays=%d), proceeding to Chartmetric", plays, min_plays)

    remix_name = parsed.get("remix_artist") or sc_track.get("user", {}).get("username")
    song_name = parsed.get("original_song")

    # Resolve the original track by ISRC first so we can use the authoritative
    # artist name from Chartmetric rather than the parsed SC title string.
    original_track = None
    if original_isrc_override:
        logger.debug("analyze_track: resolve by ISRC override %s", original_isrc_override)
        try:
            original_track = resolve_track_by_isrc(cm, original_isrc_override)
        except Exception:
            logger.warning("analyze_track: ISRC override lookup failed", exc_info=True)
            original_track = None

    # Prefer artist name from Chartmetric (via ISRC); fall back to title parser.
    if original_track and original_track.get("artist_names"):
        cm_names = original_track["artist_names"]
        original_name = " & ".join(cm_names) if len(cm_names) > 1 else cm_names[0]
        logger.debug("analyze_track: using CM artist name %r (from ISRC)", original_name)
    else:
        original_name = parsed.get("original_artist")

    logger.debug("analyze_track: enrich original+remix artists in parallel")
    with ThreadPoolExecutor(max_workers=2) as ex:
        original_future = ex.submit(_enrich_possibly_multi_artist, cm, original_name)
        remix_future = ex.submit(enrich_artist, cm, remix_name) if remix_name else None
        original_artist = original_future.result()
        remix_artist = remix_future.result() if remix_future else None

    original_geo = (original_artist or {}).get("geo_cities", [])
    remix_geo = (remix_artist or {}).get("geo_cities", [])
    original_career = (original_artist or {}).get("career", {})
    remix_career = (remix_artist or {}).get("career", {})

    projections = project_revenue(sc_metrics.get("plays", 0))
    opportunity_score = build_opportunity_score(
        sc_metrics=sc_metrics,
        original_artist=original_artist or {},
        remix_artist=remix_artist or {},
        original_geo=original_geo,
        remix_geo=remix_geo,
        original_career=original_career,
        remix_career=remix_career,
        revenue_projections=projections,
    )

    if not original_track and original_name and song_name:
        logger.debug("analyze_track: find_original_isrc for %r – %r", original_name, song_name)
        try:
            original_track = find_original_isrc(cm, original_name, song_name)
        except Exception:
            logger.warning("analyze_track: find_original_isrc failed", exc_info=True)
            original_track = None
    original_isrc = (original_track or {}).get("isrc")
    luminate_data = None
    viability = assess_viability(projections)
    logger.debug("analyze_track: done  %r  total=%.2fs", title, time.perf_counter() - _t0)

    return {
        "sc_url": norm_track.get("permalink_url"),
        "track_id": norm_track.get("id"),
        "track_title": norm_track.get("title"),
        "track_genre": norm_track.get("genre"),
        "sc_track": norm_track,
        "sc_metrics": sc_metrics,
        "parsed_title": parsed,
        "original_artist": original_artist,
        "remix_artist": remix_artist,
        "original_track": original_track,
        "original_isrc": original_isrc,
        "luminate_data": luminate_data,
        "opportunity_score": opportunity_score,
        "revenue": {"projections": projections},
        "viability": viability,
    }


def analyze_url(sc_url, clients):
    """Option 5: Analyze a single SoundCloud URL."""
    sc_track = clients["sc"].resolve(sc_url)
    return analyze_track_object(sc_track, clients)


def search_song_remixes(song_name, artist_name=None, limit=20, clients=None, min_plays=0, original_isrc=None):
    """Option 3: Search SoundCloud remixes for a specific song."""
    sc = clients["sc"]
    tracks = sc.search_remixes(song_name=song_name, artist=artist_name, limit=limit)

    # Pre-filter by playback_count from the SC search payload before calling analyze_track_object.
    # analyze_track_object also enforces this gate internally as a safety net.
    if min_plays > 0:
        before = len(tracks)
        tracks = [t for t in tracks if (t.get("playback_count") or 0) >= min_plays]
        logger.debug("search_song_remixes: %d/%d tracks passed min_plays=%d filter", len(tracks), before, min_plays)

    # No qualifying remixes — skip all Chartmetric calls entirely.
    if not tracks:
        logger.debug("search_song_remixes: no qualifying remixes for %r, skipping enrichment", song_name)
        return []

    reports = [r for r in (analyze_track_object(track, clients, original_isrc_override=original_isrc, min_plays=min_plays) for track in tracks) if r is not None]
    reports.sort(key=lambda r: r.get("opportunity_score", {}).get("overall", 0), reverse=True)
    return reports


def search_artist_remixes(artist_name, limit_songs=8, limit_remixes=6, clients=None):
    """Option 2: Build remix candidates for an artist's song set."""
    cm = clients["cm"]
    artist = cm.find_artist(artist_name)
    if not artist:
        return []

    # Practical fallback: seed songs from Chartmetric track search by artist name.
    track_seeds = cm.search(artist.get("name", artist_name), "tracks", limit=limit_songs)
    seen = set()
    reports = []
    for seed in track_seeds:
        song = seed.get("name")
        if not song or song.lower() in seen:
            continue
        seen.add(song.lower())
        song_reports = search_song_remixes(
            song_name=song,
            artist_name=artist.get("name", artist_name),
            limit=limit_remixes,
            clients=clients,
        )
        reports.extend(song_reports)

    # Deduplicate by SC track id.
    dedup = {}
    for report in reports:
        dedup[report.get("track_id")] = report
    ranked = list(dedup.values())
    ranked.sort(key=lambda r: r.get("opportunity_score", {}).get("overall", 0), reverse=True)
    return ranked


def discover_remixes(genre=None, min_plays=0, created_after=None, limit=30, clients=None):
    """Option 4: Discovery mode using search + filters."""
    sc = clients["sc"]
    tracks = sc.search_tracks(query="remix", limit=limit, genre=genre, created_after=created_after)
    tracks = [t for t in tracks if (t.get("playback_count") or 0) >= (min_plays or 0)]
    reports = [analyze_track_object(track, clients) for track in tracks]
    reports.sort(key=lambda r: r.get("opportunity_score", {}).get("overall", 0), reverse=True)
    return reports


def process_catalog(filepath, limit_remixes=5, min_plays=0, clients=None):
    """Option 1: Bulk catalog flow from CSV/XML."""
    records = parse_catalog_file(filepath)

    # Deduplicate by ISRC so the same song uploaded twice doesn't get processed twice.
    seen_isrcs: set[str] = set()
    deduped: list[dict] = []
    for r in records:
        isrc = r.get("isrc")
        if isrc:
            if isrc in seen_isrcs:
                continue
            seen_isrcs.add(isrc)
        deduped.append(r)

    all_reports = []
    for record in deduped:
        artist = record.get("artist")
        title = record.get("title")
        if not title:
            continue
        reports = search_song_remixes(
            song_name=title, artist_name=artist, limit=limit_remixes, clients=clients
        )
        if min_plays > 0:
            reports = [
                r for r in reports
                if (r.get("sc_metrics") or {}).get("plays", 0) >= min_plays
            ]
        all_reports.extend(reports)

    dedup_map = {r.get("track_id"): r for r in all_reports}
    ranked = list(dedup_map.values())
    ranked.sort(key=lambda r: r.get("opportunity_score", {}).get("overall", 0), reverse=True)
    return ranked


def make_clients():
    return {
        "sc": SoundCloudClient(),
        "cm": ChartmetricClient(),
        "lum": LuminateClient(),
    }


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Remix Radar pipeline CLI")
    parser.add_argument("url", nargs="?", help="SoundCloud URL (Option 5)")
    parser.add_argument("--song", help="Song title (Option 3)")
    parser.add_argument("--artist", help="Artist name (Option 2/3)")
    parser.add_argument("--discover", action="store_true", help="Discovery mode (Option 4)")
    parser.add_argument("--genre", help="Genre filter for discovery")
    parser.add_argument("--min-plays", type=int, default=0, help="Minimum play count for discovery")
    parser.add_argument("--created-after", help="Created-at lower bound YYYY-MM-DD")
    parser.add_argument("--limit", type=int, default=20, help="Result limit for search/discovery")
    parser.add_argument("--catalog", help="CSV/XML catalog path (Option 1)")
    parser.add_argument("--catalog-limit-remixes", type=int, default=5, help="Per-song remix limit in catalog mode")
    return parser


def main():
    _print_banner()
    _print_credentials()
    args = build_arg_parser().parse_args()
    clients = make_clients()

    try:
        if args.catalog:
            reports = process_catalog(args.catalog, limit_remixes=args.catalog_limit_remixes, clients=clients)
            print("\nCatalog Results")
            print("-" * 72)
            print(format_summary_table(reports))
            return

        if args.discover:
            reports = discover_remixes(
                genre=args.genre,
                min_plays=args.min_plays,
                created_after=args.created_after,
                limit=args.limit,
                clients=clients,
            )
            print("\nDiscovery Results")
            print("-" * 72)
            print(format_summary_table(reports))
            return

        if args.song:
            reports = search_song_remixes(
                song_name=args.song,
                artist_name=args.artist,
                limit=args.limit,
                clients=clients,
            )
            print("\nSong Search Results")
            print("-" * 72)
            print(format_summary_table(reports))
            return

        if args.artist and not args.url:
            reports = search_artist_remixes(
                artist_name=args.artist,
                limit_songs=min(args.limit, 10),
                limit_remixes=6,
                clients=clients,
            )
            print("\nArtist Search Results")
            print("-" * 72)
            print(format_summary_table(reports))
            return

        # Default / Option 5
        sc_url = args.url or DEFAULT_URL
        report = analyze_url(sc_url, clients)
        print()
        print(format_track_report(report))
    except Exception as exc:
        print("\nERROR:", exc)


if __name__ == "__main__":
    main()
