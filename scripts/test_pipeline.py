#!/usr/bin/env python3
"""
Remix Radar — End-to-End Data Pipeline Test
============================================

Tests the full data pipeline that powers Remix Radar:

    SoundCloud URL
        -> resolve track, compute engagement metrics
        -> parse title to extract original artist + song
    Chartmetric
        -> search original artist, get audience + geographic data
        -> cross-platform ID resolution (artist + track level)
        -> retrieve ISRC for original song
    Luminate
        -> look up song-level consumption data by ISRC
    Revenue Model
        -> 3-tier projection (conservative / mid / optimistic)
        -> go/no-go recommendation

Usage:
    # Run with the default test URL (Revelries' Blinding Lights remix):
    python scripts/test_pipeline.py

    # Run with a custom SoundCloud URL:
    python scripts/test_pipeline.py "https://soundcloud.com/artist/track-name"

Prerequisites:
    pip install -r requirements.txt
    .env file in project root with API credentials (see HANDOVER.md)

Team: Measure of Music 2026 Hackathon — Remix Radar
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

# ════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# SoundCloud uses an unofficial public client_id extracted from their web app.
# This is NOT an official OAuth credential — it could break at any time.
# If the hackathon provides official SoundCloud creds, replace this.
SC_CLIENT_ID = "CkCiIyf14rHi27fhk7HxhPOzc85okfSJ"
SC_BASE = "https://api-v2.soundcloud.com"

# SoundCloud's api-v2 rejects requests without browser-like headers.
# These mimic what the SoundCloud web app sends.
SC_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Referer": "https://soundcloud.com/",
    "Origin": "https://soundcloud.com",
}

CM_BASE = "https://api.chartmetric.com/api"
CM_REFRESH_TOKEN = os.getenv("CHARTMETRIC_REFRESH_TOKEN")

LUM_BASE = "https://api.luminatedata.com"
LUM_API_KEY = os.getenv("LUMINATE_API_KEY")
LUM_EMAIL = os.getenv("LUMINATE_EMAIL")
LUM_PASSWORD = os.getenv("LUMINATE_PASSWORD")

# Industry-average per-stream payout rates (USD).
# Sources: various 2024-2025 industry reports. These are rough midpoints.
STREAM_RATES = {
    "spotify": 0.004,
    "apple_music": 0.007,
    "all_dsps_avg": 0.005,
}

# How we translate SoundCloud plays into estimated DSP streams.
# These multipliers are assumptions that need calibration — see
# "remix comparison" test which attempts to derive real-world ratios.
PROJECTION_TIERS = {
    "conservative": 1.0,  # only existing SC audience converts
    "mid": 3.0,           # DSP discovery + playlist effect
    "optimistic": 5.0,    # viral / editorial playlist boost
}


# ════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ════════════════════════════════════════════════════════════════════

def _header(title):
    """Print a major section header."""
    width = 64
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def _section(title):
    """Print a subsection header."""
    print(f"\n  --- {title} ---")


def _ok(msg):
    print(f"  [OK]   {msg}")


def _fail(msg):
    print(f"  [FAIL] {msg}")


def _warn(msg):
    print(f"  [WARN] {msg}")


def _info(msg):
    print(f"         {msg}")


def _kv(key, value, indent=9):
    """Print a key-value pair with aligned formatting."""
    print(f"{' ' * indent}{key + ':':<30} {value}")


def _num(n):
    """Format a number with commas (e.g., 1,234,567)."""
    if isinstance(n, float):
        return f"{n:,.2f}"
    if n is None:
        return "N/A"
    return f"{n:,}"


def _usd(n):
    """Format a number as USD currency."""
    return f"${n:,.0f}"


# ════════════════════════════════════════════════════════════════════
# AUTH — Token management for Chartmetric and Luminate
# ════════════════════════════════════════════════════════════════════

_tokens = {}  # {"chartmetric": {"token": "...", "ts": 123456}, ...}


def _cm_token():
    """
    Get a valid Chartmetric access token.

    Chartmetric uses a two-token system:
      - A long-lived refresh token (stored in .env)
      - A short-lived access token (1 hour), obtained by POSTing the refresh token

    We cache the access token and re-fetch it after 50 minutes.
    """
    cached = _tokens.get("cm")
    if cached and (time.time() - cached["ts"]) < 3000:
        return cached["token"]

    _info("Authenticating with Chartmetric...")
    resp = requests.post(
        f"{CM_BASE}/token",
        json={"refreshtoken": CM_REFRESH_TOKEN},
    )
    resp.raise_for_status()
    token = resp.json()["token"]
    _tokens["cm"] = {"token": token, "ts": time.time()}
    return token


def _lum_token():
    """
    Get a valid Luminate access token.

    Luminate requires three credentials: API key, email, and password.
    The access token lasts 24 hours. We cache and reuse within that window.
    """
    cached = _tokens.get("lum")
    if cached and (time.time() - cached["ts"]) < 80000:
        return cached["token"]

    _info("Authenticating with Luminate...")
    resp = requests.post(
        f"{LUM_BASE}/auth",
        headers={
            "x-api-key": LUM_API_KEY,
            "content-type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        },
        data=f"username={LUM_EMAIL}&password={LUM_PASSWORD}",
    )
    resp.raise_for_status()
    body = resp.json()
    token = body.get("access_token") or body.get("token")
    _tokens["lum"] = {"token": token, "ts": time.time()}
    return token


# ════════════════════════════════════════════════════════════════════
# SOUNDCLOUD API CLIENT  (unofficial v2 — read-only, no OAuth needed)
# ════════════════════════════════════════════════════════════════════

def sc_resolve(url):
    """
    Resolve a SoundCloud permalink URL to its full track object.

    Example:
        track = sc_resolve("https://soundcloud.com/revelriesmusic/blinding_lights")
        print(track["playback_count"])  # => 4025560

    The resolved object contains all engagement fields we need:
    playback_count, likes_count, reposts_count, comment_count, created_at,
    genre, duration, user (uploader info), permalink_url, etc.
    """
    resp = requests.get(
        f"{SC_BASE}/resolve",
        params={"url": url, "client_id": SC_CLIENT_ID},
        headers=SC_HEADERS,
    )
    resp.raise_for_status()
    return resp.json()


def sc_search(query, limit=50):
    """
    Search SoundCloud for tracks matching a keyword query.

    The query searches across title, username, and description.
    Results are ordered by SoundCloud's relevance algorithm.

    Example:
        results = sc_search("blinding lights remix", limit=20)
        for t in results:
            print(t["title"], t["playback_count"])
    """
    resp = requests.get(
        f"{SC_BASE}/search/tracks",
        params={"q": query, "limit": limit, "client_id": SC_CLIENT_ID},
        headers=SC_HEADERS,
    )
    resp.raise_for_status()
    return resp.json().get("collection", [])


def sc_metrics(track):
    """
    Compute derived engagement metrics from a SoundCloud track object.

    Returns a dict with:
        plays            — raw play count (the demand signal)
        likes            — total likes
        reposts          — total reposts
        comments         — total comments
        engagement_rate  — likes / plays  (higher = more engaged audience)
        daily_velocity   — plays per day since upload date
        days_live        — how many days the track has been up
    """
    plays = track.get("playback_count") or 0
    likes = track.get("likes_count") or track.get("favoritings_count") or 0

    created = track.get("created_at", "")
    if created:
        upload_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        days = max((datetime.now(upload_dt.tzinfo) - upload_dt).days, 1)
    else:
        days = 1

    return {
        "plays": plays,
        "likes": likes,
        "reposts": track.get("reposts_count") or 0,
        "comments": track.get("comment_count") or 0,
        "engagement_rate": round(likes / plays, 4) if plays > 0 else 0,
        "daily_velocity": round(plays / days),
        "days_live": days,
    }


# ════════════════════════════════════════════════════════════════════
# CHARTMETRIC API CLIENT
# ════════════════════════════════════════════════════════════════════

def _cm_get(path, params=None):
    """
    Authenticated GET request to Chartmetric.

    Handles token refresh and enforces a 0.3s delay between calls
    to stay under the 4 requests/second rate limit.
    """
    token = _cm_token()
    time.sleep(0.3)
    resp = requests.get(
        f"{CM_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
    )
    resp.raise_for_status()
    return resp.json()


def cm_search(query, entity_type="artists", limit=5):
    """
    Search Chartmetric for artists, tracks, albums, etc.

    Returns a list of matching objects. Each artist object includes
    id (CM artist ID), name, image_url, tags, and spotify_artist_ids.
    Each track object includes id, name, isrc, artist_names, spotify_track_ids.
    """
    data = _cm_get("/search", {"q": query, "type": entity_type, "limit": limit})
    return data.get("obj", {}).get(entity_type, [])


def cm_artist(cm_id):
    """
    Get full artist metadata by Chartmetric ID.

    Key fields returned:
        name, sp_followers, sp_monthly_listeners, sp_popularity,
        tags (genres), hometown_city, code2 (country),
        spotify_artist_ids, deezer_artist_ids, etc.
    """
    return _cm_get(f"/artist/{cm_id}").get("obj", {})


def cm_where_people_listen(cm_id, since=None):
    """
    Get Spotify's "Where People Listen" geographic data for an artist.

    Returns city-level data with listener counts and affinity scores.
    Affinity > 1.0 means the city over-indexes for this artist relative
    to the city's overall streaming share.

    This is one of Chartmetric's most valuable endpoints for Remix Radar:
    it tells us WHERE demand exists, which drives marketing strategy
    for an official remix release.
    """
    if since is None:
        since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    return _cm_get(f"/artist/{cm_id}/where-people-listen", {"since": since}).get("obj", [])


def cm_artist_stat(cm_id, platform):
    """
    Get time-series fan/follower metrics for an artist on a specific platform.

    Valid platforms: spotify, soundcloud, youtube_channel, youtube_artist,
    instagram, twitter, tiktok, deezer, wikipedia, genius, shazam, etc.
    """
    return _cm_get(f"/artist/{cm_id}/stat/{platform}").get("obj", [])


def cm_artist_cross_ids(id_type, id_value):
    """
    Look up all platform IDs from one known artist ID.

    STATUS: Previously untested — this is gap #1 from the handover.

    This is the cross-platform bridge: given a Chartmetric ID, get
    Spotify, iTunes, Deezer, and Amazon IDs (or vice versa).

    Args:
        id_type:  "chartmetric", "spotify", "itunes", "deezer", "amazon"
        id_value: the known ID value

    Returns list of dicts with: cm_artist, artist_name,
    spotify_artist_id, itunes_artist_id, deezer_artist_id, amazon_artist_id
    """
    return _cm_get(f"/artist/{id_type}/{id_value}/get-ids").get("obj", [])


def cm_track(cm_id):
    """
    Get full track metadata by Chartmetric track ID.

    Key fields: name, isrc, artist_names, spotify_track_ids,
    album_label, release_dates, tags, cm_statistics.
    """
    return _cm_get(f"/track/{cm_id}").get("obj", {})


def cm_track_cross_ids(id_type, id_value):
    """
    Look up all platform IDs from one known track ID or ISRC.

    STATUS: Previously untested — this is gap #1 (continued) from the handover.

    Args:
        id_type:  "chartmetric", "isrc", "spotify", "itunes", "deezer", "amazon"
        id_value: the known ID value (e.g., an ISRC like "USUG11904189")

    Returns list of dicts with: cm_track, track_name, isrc,
    spotify_track_id, itunes_track_id, deezer_track_id, amazon_track_id
    """
    return _cm_get(f"/track/{id_type}/{id_value}/get-ids").get("obj", [])


# ════════════════════════════════════════════════════════════════════
# LUMINATE API CLIENT
# ════════════════════════════════════════════════════════════════════

def _lum_get(path, params=None):
    """Authenticated GET request to Luminate."""
    token = _lum_token()
    resp = requests.get(
        f"{LUM_BASE}{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "x-api-key": LUM_API_KEY,
            "Accept": "application/vnd.luminate-data.svc-apibff.v1+json",
        },
        params=params or {},
    )
    resp.raise_for_status()
    return resp.json()


def lum_search(query, entity_type="artist", size=10):
    """
    Search Luminate for music entities.

    GOTCHA: the `size` parameter must be >= 10, otherwise the API
    silently returns zero results. This is a known quirk.

    Valid entity_type values:
        artist, song, musical_recording, musical_release_group, musical_product
    """
    return _lum_get("/search", {
        "query": query,
        "entity_type": entity_type,
        "size": max(size, 10),
    }).get("results", [])


def lum_song(isrc, location="US", start_date=None, end_date=None):
    """
    Get song-level metadata and consumption data by ISRC.

    STATUS: Previously untested — this is gap #2 from the handover.

    A "song" in Luminate is a composition that may group multiple recordings.
    This endpoint returns stream counts, sales, and other metrics
    for the specified territory and date range.

    Args:
        isrc:       ISRC code (e.g., "USUG11904189")
        location:   ISO country code (default "US")
        start_date: YYYY-MM-DD (default: 90 days ago)
        end_date:   YYYY-MM-DD (default: today)
    """
    if not start_date:
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    return _lum_get(f"/songs/{isrc}", {
        "id_type": "isrc",
        "metrics": "all",
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "metadata_level": "max",
    })


def lum_recording(isrc, location="US", start_date=None, end_date=None):
    """
    Get recording-level metadata and consumption data by ISRC.

    A "recording" is the most granular entity — a specific master
    identified by its ISRC. This is more specific than a "song"
    (which can group multiple recordings of the same composition).
    """
    if not start_date:
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    return _lum_get(f"/musical_recordings/{isrc}", {
        "id_type": "isrc",
        "metrics": "all",
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "metadata_level": "max",
    })


# ════════════════════════════════════════════════════════════════════
# REMIX TITLE PARSER
# ════════════════════════════════════════════════════════════════════

# Matches parentheticals like "(Virtu Remix)", "(DJ Snake Edit)",
# "(Bootleg)", "(VIP Mix)", "(Festival Rework)"
_REMIX_PAREN = re.compile(
    r"\s*\(([^)]+?)\s+(?:remix|edit|bootleg|flip|rework|vip|mix)\)",
    re.IGNORECASE,
)

# Matches bracket variants like "[Remix]"
_REMIX_BRACKET = re.compile(
    r"\s*\[([^\]]+?)\s+(?:remix|edit|bootleg|flip|rework|vip|mix)\]",
    re.IGNORECASE,
)


def parse_remix_title(title):
    """
    Extract original artist, original song, and remix artist from a
    SoundCloud track title.

    SoundCloud has NO structured "remix of" metadata, so we have to parse
    freeform text. This is inherently fragile — the weakest link in the
    pipeline. Common title patterns:

        "Artist - Song Title (RemixArtist Remix)"
        "Artist - Song Title [RemixArtist Edit]"
        "RemixArtist - Song Title (Remix)"
        "Song Title (RemixArtist Bootleg)"

    Returns dict with:
        original_artist  — best guess (None if not parseable)
        original_song    — best guess
        remix_artist     — extracted from parenthetical (None if not found)
        raw_title        — the unmodified input
    """
    result = {
        "original_artist": None,
        "original_song": None,
        "remix_artist": None,
        "raw_title": title,
    }

    # 1. Try to extract the remix/cover artist from parentheses or brackets.
    #    Also handle "Cover Remix" patterns like "(Weeknd Cover Remix)"
    #    where the name inside is actually the ORIGINAL artist, not the remixer.
    match = _REMIX_PAREN.search(title) or _REMIX_BRACKET.search(title)
    is_cover = False
    if match:
        inner = match.group(1).strip()
        if re.search(r"\bcover\b", inner, re.IGNORECASE):
            # "(Weeknd Cover)" or "(Weeknd Cover Remix)" — the name is the
            # original artist, and the person before " - " is the remixer.
            is_cover = True
            result["remix_artist"] = None  # will be filled from the "Artist - " part
            # Extract the original artist name from within the parenthetical
            cover_name = re.sub(r"\s+cover\b.*$", "", inner, flags=re.IGNORECASE).strip()
            if cover_name:
                result["original_artist"] = cover_name
        else:
            result["remix_artist"] = inner

    # 2. Strip the remix/cover parenthetical to isolate the core title
    clean = _REMIX_PAREN.sub("", title)
    clean = _REMIX_BRACKET.sub("", clean).strip()
    clean = re.sub(r"\s*[-–]\s*(?:remix|edit|bootleg|flip|rework)$", "", clean, flags=re.IGNORECASE).strip()

    # 3. Split on " - " or " – " to separate artist from song
    for sep in (" - ", " – ", " — "):
        if sep in clean:
            parts = clean.split(sep, 1)
            if is_cover:
                # In a cover remix, the left side of " - " is the remixer,
                # not the original artist.
                result["remix_artist"] = parts[0].strip()
            else:
                result["original_artist"] = parts[0].strip()
            result["original_song"] = parts[1].strip()
            return result

    # 4. Fallback: entire cleaned string is the song name
    result["original_song"] = clean
    return result


# ════════════════════════════════════════════════════════════════════
# REVENUE PROJECTION MODEL
# ════════════════════════════════════════════════════════════════════

def project_revenue(sc_plays):
    """
    Generate 3-tier revenue projections from a SoundCloud play count.

    The model:
        estimated_dsp_streams = sc_plays x multiplier
        revenue = estimated_dsp_streams x per_stream_rate

    The multipliers (1x / 3x / 5x) are assumptions based on the idea
    that a remix's SoundCloud audience is a subset of the total
    addressable market on DSPs. These need calibration against real
    cases — see the remix comparison test.

    Returns a dict keyed by tier name, each containing:
        estimated_streams  — projected DSP streams
        revenue            — dict of revenue by platform
    """
    result = {}
    for tier, mult in PROJECTION_TIERS.items():
        streams = int(sc_plays * mult)
        result[tier] = {
            "estimated_streams": streams,
            "revenue": {
                platform: round(streams * rate, 2)
                for platform, rate in STREAM_RATES.items()
            },
        }
    return result


# ════════════════════════════════════════════════════════════════════
# TEST ROUTINES
#
# Each test_* function exercises one piece of the pipeline,
# prints human-readable output, and returns the data for chaining.
# ════════════════════════════════════════════════════════════════════

def test_soundcloud_resolve(url):
    """
    TEST 1 — SoundCloud: resolve a URL and compute engagement metrics.

    This is the entry point of the entire pipeline. We take a SoundCloud
    URL, resolve it to a track object, and compute derived metrics like
    engagement rate and daily velocity.
    """
    _header("TEST 1: SoundCloud — Resolve URL & Compute Metrics")
    _info(f"URL: {url}")

    track = sc_resolve(url)
    if not track or not track.get("id"):
        _fail("Empty response from SoundCloud. Check the URL.")
        return None

    _ok(f"Resolved: \"{track['title']}\"")
    _kv("Artist", track.get("user", {}).get("username", "Unknown"))
    _kv("Genre", track.get("genre") or "N/A")
    _kv("Track ID", track.get("id"))
    _kv("Permalink", track.get("permalink_url"))

    metrics = sc_metrics(track)
    _section("Engagement Metrics")
    _kv("Plays", _num(metrics["plays"]))
    _kv("Likes", _num(metrics["likes"]))
    _kv("Reposts", _num(metrics["reposts"]))
    _kv("Comments", _num(metrics["comments"]))
    _kv("Engagement Rate", f"{metrics['engagement_rate']:.2%}")
    _kv("Daily Velocity", f"{_num(metrics['daily_velocity'])} plays/day")
    _kv("Days Live", f"{metrics['days_live']} days")

    parsed = parse_remix_title(track["title"])
    _section("Parsed Title")
    _kv("Original Artist", parsed["original_artist"] or "(could not detect)")
    _kv("Original Song", parsed["original_song"] or "(could not detect)")
    _kv("Remix Artist", parsed["remix_artist"] or "(could not detect)")

    track["_metrics"] = metrics
    track["_parsed"] = parsed
    return track


def test_chartmetric_enrich(artist_name, track_name=None):
    """
    TEST 2 — Chartmetric: search for the original artist and pull
    audience data, geographic listeners, and (optionally) track ISRC.

    This validates that we can bridge from a name string (parsed from
    the SoundCloud title) into Chartmetric's structured data.
    """
    _header("TEST 2: Chartmetric — Artist Search & Enrichment")
    _info(f"Searching for: \"{artist_name}\"")

    # Collect candidates from multiple search variants, then pick the best.
    # This handles cases like "Weeknd" vs. "The Weeknd" where the top
    # search result for the parsed name is a small artist, not the star.
    search_variants = [artist_name, f"The {artist_name}", f"DJ {artist_name}"]
    all_candidates = []
    for variant in search_variants:
        results = cm_search(variant, "artists", limit=5)
        all_candidates.extend(results)

    if not all_candidates:
        _fail(f"No Chartmetric results for \"{artist_name}\" (or variants)")
        return None

    # Rank by cm_artist_score (Chartmetric's own ranking of artist prominence).
    # Higher score = more prominent artist = more likely to be correct.
    all_candidates.sort(key=lambda a: a.get("cm_artist_score") or 0, reverse=True)

    # De-duplicate by CM ID
    seen = set()
    unique = []
    for c in all_candidates:
        if c["id"] not in seen:
            seen.add(c["id"])
            unique.append(c)

    top = unique[0]
    cm_id = top["id"]
    score = top.get("cm_artist_score", 0)
    _ok(f"Found: {top.get('name')} (CM ID: {cm_id}, score: {score:.1f})")
    if top.get("name", "").lower() != artist_name.lower():
        _info(f"(parsed name was \"{artist_name}\" — matched to \"{top.get('name')}\")")

    # Full metadata — combine search result (has Spotify counts)
    # with full endpoint (has career_status, genres, label, etc.)
    meta = cm_artist(cm_id)
    _section("Artist Metadata")

    # Spotify metrics come from the search result, not the full endpoint
    _kv("Spotify Followers", _num(top.get("sp_followers")))
    _kv("Spotify Monthly Listeners", _num(top.get("sp_monthly_listeners")))
    _kv("CM Artist Rank", meta.get("cm_artist_rank", "N/A"))

    career = meta.get("career_status", {})
    if career:
        _kv("Career Stage", f"{career.get('stage', '?')} (trend: {career.get('trend', '?')})")

    genres = meta.get("genres", {})
    primary = genres.get("primary", {}) if isinstance(genres, dict) else {}
    _kv("Primary Genre", primary.get("name", "N/A") if isinstance(primary, dict) else "N/A")
    _kv("Record Label", meta.get("record_label") or "N/A")
    _kv("Hometown", meta.get("hometown_city") or "N/A")
    _kv("Country", meta.get("code2") or "N/A")

    # Geographic listeners — the response is structured as:
    # { "cities": { "CityName": [{ listeners, code2, city_affinity, ... }], ... },
    #   "countries": { ... } }
    _section("Where People Listen (Top 5 Cities)")
    geo = cm_where_people_listen(cm_id)
    city_list = []
    if isinstance(geo, dict) and "cities" in geo:
        for city_name, entries in geo["cities"].items():
            if entries:
                entry = entries[0]  # most recent data point
                city_list.append({
                    "name": city_name,
                    "code2": entry.get("code2", ""),
                    "listeners": entry.get("listeners", 0),
                    "affinity": entry.get("city_affinity", 0),
                })
        city_list.sort(key=lambda c: c["listeners"], reverse=True)
        for c in city_list[:5]:
            _info(f"{c['name']} ({c['code2']}): {_num(c['listeners'])} listeners, "
                  f"affinity {c['affinity']:.2f}")
    elif isinstance(geo, list) and geo:
        for city in geo[:5]:
            _info(f"{city.get('name', '?')} ({city.get('code2', '')}): "
                  f"{_num(city.get('listeners', 0))} listeners")
        city_list = geo
    else:
        _warn(f"Unexpected geo response format: {type(geo).__name__}")
        _info(f"Raw (first 200 chars): {str(geo)[:200]}")

    # Track lookup: try multiple strategies to find the original track's ISRC
    track_data = None
    if track_name:
        _section(f"Track Search: \"{track_name}\"")

        # Strategy 1: Search by "artist song" combined
        search_queries = [
            f"{meta.get('name', artist_name)} {track_name}",
            track_name,
        ]
        tracks = []
        for sq in search_queries:
            _info(f"Trying query: \"{sq}\"")
            tracks = cm_search(sq, "tracks", limit=5)
            if tracks:
                # Try to find one whose artist list includes our artist
                artist_lower = (meta.get("name") or artist_name).lower()
                for t in tracks:
                    t_artists = [a.lower() for a in (t.get("artist_names") or [])]
                    if any(artist_lower in a or a in artist_lower for a in t_artists):
                        tracks = [t]  # prioritize this match
                        break
                break

        if tracks:
            t = tracks[0]
            cm_track_id = t["id"]
            _ok(f"Found: \"{t.get('name')}\" by {t.get('artist_names', [])} (CM Track ID: {cm_track_id})")
            _kv("ISRC", t.get("isrc") or "N/A")

            full = cm_track(cm_track_id)
            labels = full.get("album_label", [])
            if isinstance(labels, str):
                labels = [labels]
            track_data = {
                "cm_track_id": cm_track_id,
                "isrc": full.get("isrc"),
                "name": full.get("name"),
                "artist_names": full.get("artist_names", []),
                "spotify_track_ids": full.get("spotify_track_ids", []),
                "album_label": labels,
            }
            _kv("Spotify Track IDs", track_data["spotify_track_ids"] or "None")
            _kv("Label", ", ".join(labels) if labels else "N/A")
        else:
            _warn(f"Track not found via Chartmetric search (search can be unreliable)")
            _info("Tip: if you know the ISRC, you can use cm_track_cross_ids('isrc', ISRC) directly")

    return {"cm_id": cm_id, "artist": meta, "geo": geo, "track": track_data}


def test_cross_platform_ids(cm_id):
    """
    TEST 3 — Chartmetric: cross-platform artist ID resolution.

    STATUS: Previously untested (gap #1 from handover).

    Given a Chartmetric artist ID, retrieve the corresponding IDs on
    Spotify, iTunes/Apple Music, Deezer, and Amazon Music.
    This is the bridge that lets us link an artist across platforms.
    """
    _header("TEST 3: Chartmetric — Cross-Platform Artist IDs  [GAP #1]")
    _info(f"CM Artist ID: {cm_id}")

    try:
        ids = cm_artist_cross_ids("chartmetric", str(cm_id))
    except requests.HTTPError as e:
        _fail(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
        return None

    if not ids:
        _warn("Empty response — endpoint may use a different response format")
        return None

    _ok(f"Retrieved {len(ids)} ID mapping(s)")
    for entry in ids[:5]:
        if isinstance(entry, dict):
            _info(f"  CM: {entry.get('cm_artist', '?')}  "
                  f"Spotify: {entry.get('spotify_artist_id', 'N/A')}  "
                  f"iTunes: {entry.get('itunes_artist_id', 'N/A')}  "
                  f"Deezer: {entry.get('deezer_artist_id', 'N/A')}  "
                  f"Amazon: {entry.get('amazon_artist_id', 'N/A')}")
        else:
            _info(f"  {entry}")

    return ids


def test_track_ids_by_isrc(isrc):
    """
    TEST 4 — Chartmetric: cross-platform track ID resolution by ISRC.

    STATUS: Previously untested (gap #1 continued from handover).

    Given an ISRC, retrieve the Chartmetric track ID plus Spotify,
    iTunes, Deezer, and Amazon track IDs. This is how we verify
    whether a remix already exists on DSPs (and if so, get its
    Spotify track ID for further analysis).
    """
    _header("TEST 4: Chartmetric — Track IDs by ISRC  [GAP #1 cont.]")
    _info(f"ISRC: {isrc}")

    try:
        ids = cm_track_cross_ids("isrc", isrc)
    except requests.HTTPError as e:
        _fail(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
        return None

    if not ids:
        _warn("Empty response — ISRC may not be in Chartmetric's database")
        return None

    _ok(f"Retrieved {len(ids)} track mapping(s)")
    for entry in ids[:5]:
        if isinstance(entry, dict):
            _info(f"  CM Track: {entry.get('cm_track', '?')}  "
                  f"Name: \"{entry.get('track_name', '?')}\"  "
                  f"Spotify: {entry.get('spotify_track_id', 'N/A')}")
        else:
            _info(f"  {entry}")

    return ids


def test_luminate_isrc(isrc, label=""):
    """
    TEST 5 — Luminate: song/recording lookup by ISRC.

    STATUS: Previously untested (gap #2 from handover).

    Attempts to retrieve consumption data (streams, sales) for a song
    identified by its ISRC. Tries the /songs/ endpoint first; if that
    fails, falls back to /musical_recordings/.

    This is how we get real DSP stream counts for the original song,
    which lets us benchmark the remix's projected performance.
    """
    _header(f"TEST 5: Luminate — ISRC Lookup  [GAP #2]  {label}")
    _info(f"ISRC: {isrc}")

    def _try_endpoint(path_fn, endpoint_name):
        """Try a Luminate endpoint, return data or None."""
        try:
            data = path_fn(isrc)
            if data.get("message") is None and len(data) <= 1:
                _warn(f"{endpoint_name} returned empty/null response (API may be down)")
                return None
            title = data.get("title", "N/A")
            artist = data.get("display_artist_name", "N/A")
            _ok(f"{endpoint_name} returned: \"{title}\" by {artist}")

            metrics = data.get("metrics", [])
            if metrics:
                _section("Consumption Data (US, last 90 days)")
                for m in metrics:
                    name = m.get("metric_name") or m.get("name") or "unknown"
                    val = m.get("value", 0)
                    _kv(name, _num(val))
            else:
                _warn("No metrics in response")
                _info(f"Response keys: {list(data.keys())}")
                _info(f"Sample: {json.dumps(data, default=str)[:300]}")
            return data
        except requests.HTTPError as e:
            status = e.response.status_code
            if status == 500:
                _warn(f"{endpoint_name} returned HTTP 500 (Luminate API may be down)")
            else:
                _warn(f"{endpoint_name} returned HTTP {status}")
            _info(f"Response: {e.response.text[:200]}")
            return None

    # Try /songs/ first, then fall back to /musical_recordings/
    result = _try_endpoint(lum_song, "/songs/")
    if result:
        return result

    _info("Trying /musical_recordings/ endpoint instead...")
    result = _try_endpoint(lum_recording, "/musical_recordings/")
    if result:
        return result

    _fail("Both Luminate endpoints failed.")
    _info("If all Luminate endpoints return 500, the service is likely down.")
    _info("This does not block the rest of the pipeline — revenue projections")
    _info("will use the SoundCloud-based model instead of Luminate benchmarks.")
    return None


def test_revenue_projection(sc_plays, track_title=""):
    """
    TEST 6 — Revenue projection from SoundCloud play count.

    Applies the 3-tier model and prints a formatted table.
    Also checks the mid-tier revenue against a $50K viability threshold
    to generate a go/no-go recommendation.
    """
    _header("TEST 6: Revenue Projection")
    _info(f"SoundCloud plays: {_num(sc_plays)}")
    if track_title:
        _info(f"Track: \"{track_title}\"")

    proj = project_revenue(sc_plays)

    _section("Projected Revenue")
    row_fmt = "  {:<15} {:>18} {:>14} {:>14} {:>14}"
    print(row_fmt.format("Tier", "Est. DSP Streams", "Spotify", "Apple Music", "All DSPs"))
    print(f"  {'-' * 75}")
    for tier, data in proj.items():
        s = data["estimated_streams"]
        r = data["revenue"]
        print(row_fmt.format(
            tier,
            _num(s),
            _usd(r["spotify"]),
            _usd(r["apple_music"]),
            _usd(r["all_dsps_avg"]),
        ))

    viability = 50_000
    mid_rev = proj["mid"]["revenue"]["all_dsps_avg"]
    _section("Viability Assessment")
    if mid_rev >= viability:
        _ok(f"CLEARS ${_num(viability)} threshold at mid tier (${_num(int(mid_rev))})")
        _info("Recommendation: This remix warrants clearance evaluation.")
    else:
        _warn(f"BELOW ${_num(viability)} threshold at mid tier (${_num(int(mid_rev))})")
        _info("Recommendation: May not justify clearance costs at current engagement.")

    return proj


# ════════════════════════════════════════════════════════════════════
# FULL PIPELINE ORCHESTRATOR
# ════════════════════════════════════════════════════════════════════

def run_pipeline(sc_url):
    """
    Run the complete Remix Radar pipeline from a SoundCloud URL
    to a final revenue projection and go/no-go recommendation.

    Steps:
        1. Resolve SC URL -> track data + engagement metrics
        2. Parse remix title -> original artist & song name
        3. Search Chartmetric for original artist -> metadata + geo
        4. Test cross-platform artist ID resolution (gap #1)
        5. Search Chartmetric for original track -> get ISRC
        6. Test cross-platform track ID resolution by ISRC (gap #1 cont.)
        7. Look up original song in Luminate by ISRC (gap #2)
        8. Compute revenue projections
        9. Print summary with pass/fail status for each step
    """
    _header("FULL PIPELINE: SoundCloud URL -> Remix Radar Report")
    _info(f"Input: {sc_url}")
    _info(f"Time:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    passed = []
    failed = []

    # ── Step 1: SoundCloud ──────────────────────────────────────────
    track = test_soundcloud_resolve(sc_url)
    if not track:
        failed.append("soundcloud_resolve")
        _fail("Pipeline cannot continue without SoundCloud data.")
        return {"passed": passed, "failed": failed}
    passed.append("soundcloud_resolve")

    parsed = track["_parsed"]
    original_artist = parsed["original_artist"]
    original_song = parsed["original_song"]

    # ── Step 2: Chartmetric — original artist enrichment ────────────
    cm_data = None
    search_artist = original_artist
    if not search_artist:
        _warn("Could not parse original artist — searching by song title instead")
        search_artist = original_song

    if search_artist:
        cm_data = test_chartmetric_enrich(search_artist, original_song)

    if cm_data:
        passed.append("chartmetric_artist_enrich")
    else:
        failed.append("chartmetric_artist_enrich")

    # ── Step 3: Chartmetric — cross-platform artist IDs (gap #1) ───
    if cm_data:
        cross_ids = test_cross_platform_ids(cm_data["cm_id"])
        if cross_ids:
            passed.append("chartmetric_cross_platform_artist_ids")
        else:
            failed.append("chartmetric_cross_platform_artist_ids")

    # ── Step 4: Chartmetric — track ISRC + cross-platform (gap #1) ─
    isrc = None
    # First check if the SoundCloud track itself has ISRC in publisher_metadata
    sc_isrc = (track.get("publisher_metadata") or {}).get("isrc")
    if sc_isrc:
        _info(f"SoundCloud track has ISRC in metadata: {sc_isrc} (this is the REMIX's ISRC)")

    # For Luminate lookup, we want the ORIGINAL song's ISRC (from Chartmetric)
    if cm_data and cm_data.get("track") and cm_data["track"].get("isrc"):
        isrc = cm_data["track"]["isrc"]
        track_ids = test_track_ids_by_isrc(isrc)
        if track_ids:
            passed.append("chartmetric_track_ids_by_isrc")
        else:
            failed.append("chartmetric_track_ids_by_isrc")
    else:
        _warn("No original song ISRC found via Chartmetric track search")
        _info("Chartmetric's track search can be unreliable for very popular songs.")
        _info("Workaround: use a known ISRC directly with cm_track_cross_ids().")
        failed.append("no_isrc_available")

    # ── Step 5: Luminate — song consumption by ISRC (gap #2) ───────
    if isrc:
        lum_data = test_luminate_isrc(isrc, label=f"[\"{original_song}\"]")
        if lum_data:
            passed.append("luminate_isrc_lookup")
        else:
            failed.append("luminate_isrc_lookup")
    else:
        _info("Skipping Luminate lookup (no ISRC)")
        failed.append("luminate_skipped_no_isrc")

    # ── Step 6: Revenue projection ─────────────────────────────────
    sc_plays = track["_metrics"]["plays"]
    projections = test_revenue_projection(sc_plays, track["title"])
    passed.append("revenue_projection")

    # ── Summary ────────────────────────────────────────────────────
    _header("PIPELINE SUMMARY")
    total = len(passed) + len(failed)
    print(f"\n  Steps passed: {len(passed)} / {total}")
    for s in passed:
        _ok(s)
    if failed:
        print(f"\n  Steps failed: {len(failed)} / {total}")
        for s in failed:
            _fail(s)

    return {
        "passed": passed,
        "failed": failed,
        "sc_track": track,
        "cm_data": cm_data,
        "isrc": isrc,
        "projections": projections,
    }


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 64)
    print("  Remix Radar — Data Pipeline Test Suite")
    print("  Measure of Music 2026 Hackathon")
    print("=" * 64)
    print(f"  Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Python: {sys.version.split()[0]}")

    # ── Credential check ───────────────────────────────────────────
    _section("Credential Check")
    all_ok = True
    for name, val in [
        ("CHARTMETRIC_REFRESH_TOKEN", CM_REFRESH_TOKEN),
        ("LUMINATE_API_KEY", LUM_API_KEY),
        ("LUMINATE_EMAIL", LUM_EMAIL),
        ("SOUNDCLOUD_CLIENT_ID", SC_CLIENT_ID),
    ]:
        if val:
            _ok(f"{name} loaded")
        else:
            _fail(f"{name} MISSING — check .env")
            all_ok = False

    if not all_ok:
        print("\n  Cannot proceed with missing credentials.")
        sys.exit(1)

    # ── Pick test URL ──────────────────────────────────────────────
    # Default: Revelries' Blinding Lights remix (known good from previous testing)
    test_url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://soundcloud.com/revelriesmusic/blinding_lights"
    )

    # ── Run ────────────────────────────────────────────────────────
    results = run_pipeline(test_url)

    print("\n" + "=" * 64)
    print("  Test suite complete.")
    print("=" * 64)
