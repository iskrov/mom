#!/usr/bin/env python3
"""
Remix Radar pipeline orchestrator and reusable workflow service layer.

This module now exposes reusable analysis functions suitable for both:
- CLI workflows (current hackathon usage)
- future FastAPI endpoints (planned)
"""

import argparse
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
    geo_raw = cm.get_where_people_listen(cm_id)
    cities = cm.parse_geo_data(geo_raw)
    ids = cm.get_artist_platform_ids(cm_id)
    platform_ids = ids[0] if isinstance(ids, list) and ids else (ids or {})

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
    query = f"{artist_name} {song_name}"
    tracks = cm.search(query, "tracks", limit=5)
    if not tracks:
        return None
    top = tracks[0]
    full = cm.get_track(top.get("id"))
    isrc = full.get("isrc") or top.get("isrc")
    return {
        "cm_track_id": top.get("id"),
        "name": full.get("name") or top.get("name"),
        "isrc": isrc,
        "artist_names": full.get("artist_names") or top.get("artist_names") or [],
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


def analyze_track_object(sc_track, clients):
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

    opportunity_score = build_opportunity_score(
        sc_metrics=sc_metrics,
        original_artist=original_artist or {},
        remix_artist=remix_artist or {},
        original_geo=original_geo,
        remix_geo=remix_geo,
        original_career=original_career,
        remix_career=remix_career,
    )

    original_track = find_original_isrc(cm, original_name, song_name) if original_name and song_name else None
    original_isrc = (original_track or {}).get("isrc")
    luminate_data = fetch_luminate_by_isrc(lum, original_isrc)
    projections = project_revenue(sc_metrics.get("plays", 0))
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


def process_catalog(filepath, limit_remixes=5, clients=None):
    """Option 1: Bulk catalog flow from CSV/XML."""
    records = parse_catalog_file(filepath)
    all_reports = []
    for record in records:
        artist = record.get("artist")
        title = record.get("title")
        if not title:
            continue
        reports = search_song_remixes(
            song_name=title, artist_name=artist, limit=limit_remixes, clients=clients
        )
        all_reports.extend(reports)
    dedup = {r.get("track_id"): r for r in all_reports}
    ranked = list(dedup.values())
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
