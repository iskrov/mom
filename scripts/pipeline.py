#!/usr/bin/env python3
"""
Remix Radar pipeline orchestrator and reusable workflow service layer.

This module now exposes reusable analysis functions suitable for both:
- CLI workflows (current hackathon usage)
- future FastAPI endpoints (planned)
"""

import argparse
import re
from datetime import datetime

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
            return None
        cm_track_id = cm_ids[0]
        full = cm.get_track(cm_track_id) or {}
    except Exception:
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

    return {
        "cm_track_id": cm_track_id,
        "name": full.get("name"),
        "isrc": full.get("isrc") or clean_isrc,
        "artist_names": full.get("artist_names") or [],
        "release_date": _extract_release_date(full),
        "songwriters": _extract_songwriters(full),
        "album_label": full.get("album_label"),
        "album_record_label": album_record_label,
        "track_record_label": full.get("record_label") or full.get("label"),
        "match_confidence": 1.0,
    }


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
    search_result = cm.find_artist(artist_name)
    if not search_result:
        return None

    cm_id = search_result.get("id")
    meta = cm.get_artist(cm_id)
    career = {}
    try:
        career = cm.get_artist_career(cm_id)
    except Exception:
        # Career is helpful but optional for resilience.
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

    return {
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


def find_original_isrc(cm, artist_name, song_name):
    """Find likely original track ISRC via Chartmetric track search."""
    if not artist_name or not song_name:
        return None

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
        return None

    scored = sorted(
        [{"track": track, "score": _score_track_candidate(track)} for track in tracks],
        key=lambda row: row["score"],
        reverse=True,
    )
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


def analyze_track_object(sc_track, clients, original_isrc_override=None):
    """
    Core reusable per-track analysis function.

    This is the API-ready service function that all workflows call.
    """
    sc = clients["sc"]
    cm = clients["cm"]
    lum = clients["lum"]

    norm_track = normalize_sc_track(sc_track)
    parsed = parse_remix_title(norm_track["title"] or "")
    sc_metrics = sc.compute_metrics(sc_track)

    original_name = parsed.get("original_artist")
    remix_name = parsed.get("remix_artist") or sc_track.get("user", {}).get("username")
    song_name = parsed.get("original_song")

    original_artist = enrich_artist(cm, original_name) if original_name else None
    remix_artist = enrich_artist(cm, remix_name) if remix_name else None

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

    original_track = None
    if original_isrc_override:
        original_track = resolve_track_by_isrc(cm, original_isrc_override)
    if not original_track and original_name and song_name:
        original_track = find_original_isrc(cm, original_name, song_name)
    original_isrc = (original_track or {}).get("isrc")
    luminate_data = fetch_luminate_by_isrc(lum, original_isrc)
    viability = assess_viability(projections)

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


def search_song_remixes(song_name, artist_name=None, limit=20, clients=None):
    """Option 3: Search SoundCloud remixes for a specific song."""
    sc = clients["sc"]
    tracks = sc.search_remixes(song_name=song_name, artist=artist_name, limit=limit)
    reports = [analyze_track_object(track, clients) for track in tracks]
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
