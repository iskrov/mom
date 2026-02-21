#!/usr/bin/env python3
"""
Remix Radar -- Main Pipeline Orchestrator.

Chains all platform clients together to produce a full remix
evaluation report from a single SoundCloud URL.

Usage:
    python -m scripts.pipeline "https://soundcloud.com/artist/track"
"""

import sys
from datetime import datetime

import requests

from scripts.config import cfg
from scripts.models import assess_viability, parse_remix_title, project_revenue
from scripts.platforms import ChartmetricClient, LuminateClient, SoundCloudClient


def _header(t):
    print("\n" + "=" * 64 + "\n  " + t + "\n" + "=" * 64)


def _section(t):
    print("\n  --- " + t + " ---")


def _ok(m):
    print("  [OK]   " + m)


def _fail(m):
    print("  [FAIL] " + m)


def _warn(m):
    print("  [WARN] " + m)


def _info(m):
    print("         " + m)


def _kv(k, v, indent=9):
    label = k + ":"
    print(" " * indent + "{:<30} {}".format(label, v))


def _num(n):
    if n is None:
        return "N/A"
    if isinstance(n, float):
        return "{:,.2f}".format(n)
    return "{:,}".format(n)


def _usd(n):
    return "${:,.0f}".format(n)


def step_soundcloud(sc, url):
    """Step 1: Resolve SoundCloud URL and compute engagement metrics."""
    _header("STEP 1: SoundCloud -- Resolve and Analyze")
    _info("URL: " + url)

    try:
        track = sc.resolve(url)
    except requests.HTTPError as e:
        _fail("HTTP {} -- check the URL".format(e.response.status_code))
        return None
    if not track or not track.get("id"):
        _fail("Empty response. Check the URL.")
        return None

    _ok("Resolved: " + repr(track["title"]))
    _kv("Artist", track.get("user", {}).get("username", "?"))
    _kv("Genre", track.get("genre") or "N/A")
    _kv("Track ID", str(track.get("id")))

    metrics = sc.compute_metrics(track)
    _section("Engagement Metrics")
    _kv("Plays", _num(metrics["plays"]))
    _kv("Likes", _num(metrics["likes"]))
    _kv("Reposts", _num(metrics["reposts"]))
    _kv("Comments", _num(metrics["comments"]))
    _kv("Engagement Rate", "{:.2%}".format(metrics["engagement_rate"]))
    _kv("Daily Velocity", _num(metrics["daily_velocity"]) + " plays/day")
    _kv("Days Live", str(metrics["days_live"]) + " days")

    parsed = parse_remix_title(track["title"])
    _section("Parsed Title")
    _kv("Original Artist", parsed["original_artist"] or "(not detected)")
    _kv("Original Song", parsed["original_song"] or "(not detected)")
    _kv("Remix Artist", parsed["remix_artist"] or "(not detected)")

    sc_isrc = sc.extract_isrc(track)
    if sc_isrc:
        _kv("Remix ISRC (from SC)", sc_isrc)

    return {
        "track": track,
        "metrics": metrics,
        "parsed": parsed,
        "remix_isrc": sc_isrc,
    }


def step_chartmetric_artist(cm, artist_name, track_name=None):
    """Step 2: Search Chartmetric for the original artist + enrichment."""
    _header("STEP 2: Chartmetric -- Artist Enrichment")
    _info("Searching for: " + repr(artist_name))

    search_result = cm.find_artist(artist_name)
    if not search_result:
        _fail("No Chartmetric results for " + repr(artist_name))
        return None

    cm_id = search_result["id"]
    score = search_result.get("cm_artist_score", 0)
    _ok("{} (CM ID: {}, score: {:.1f})".format(
        search_result.get("name", "?"), cm_id, score))
    if search_result.get("name", "").lower() != artist_name.lower():
        _info("(parsed as {}, matched to {})".format(
            repr(artist_name), repr(search_result["name"])))

    meta = cm.get_artist(cm_id)
    _section("Artist Metadata")
    _kv("Spotify Followers", _num(search_result.get("sp_followers")))
    _kv("Spotify Monthly Listeners", _num(search_result.get("sp_monthly_listeners")))
    _kv("CM Artist Rank", str(meta.get("cm_artist_rank", "N/A")))
    career = meta.get("career_status", {})
    if career:
        _kv("Career Stage", "{} ({})".format(
            career.get("stage", "?"), career.get("trend", "?")))
    genres = meta.get("genres", {})
    primary = genres.get("primary", {}) if isinstance(genres, dict) else {}
    gname = primary.get("name", "N/A") if isinstance(primary, dict) else "N/A"
    _kv("Primary Genre", gname)
    _kv("Record Label", meta.get("record_label") or "N/A")
    _kv("Hometown", meta.get("hometown_city") or "N/A")

    _section("Where People Listen (Top 5)")
    geo_raw = cm.get_where_people_listen(cm_id)
    cities = cm.parse_geo_data(geo_raw)
    for c in cities[:5]:
        _info("{} ({}): {} listeners, affinity {:.2f}".format(
            c["name"], c["code2"], _num(c["listeners"]), c["affinity"]))

    track_data = None
    if track_name:
        _section("Track Search: " + repr(track_name))
        query = meta.get("name", artist_name) + " " + track_name
        tracks = cm.search(query, "tracks", limit=5)
        if tracks:
            t = tracks[0]
            _ok("Found: {} (CM Track ID: {})".format(
                repr(t.get("name", "?")), t["id"]))
            _kv("ISRC", t.get("isrc") or "N/A")
            full = cm.get_track(t["id"])
            track_data = {
                "cm_track_id": t["id"],
                "isrc": full.get("isrc"),
                "name": full.get("name"),
                "artist_names": full.get("artist_names", []),
            }
        else:
            _warn("Track not found via Chartmetric search")

    return {
        "cm_id": cm_id,
        "search_result": search_result,
        "artist_meta": meta,
        "cities": cities,
        "track": track_data,
    }


def step_chartmetric_ids(cm, cm_id, isrc=None):
    """Step 3: Cross-platform ID resolution."""
    _header("STEP 3: Chartmetric -- Cross-Platform IDs")

    _info("Artist IDs for CM {}...".format(cm_id))
    artist_ids = None
    try:
        artist_ids = cm.get_artist_platform_ids(cm_id)
        if artist_ids:
            top = artist_ids[0] if isinstance(artist_ids, list) else artist_ids
            _ok("Spotify: {}, iTunes: {}, Deezer: {}".format(
                top.get("spotify_artist_id", "N/A"),
                top.get("itunes_artist_id", "N/A"),
                top.get("deezer_artist_id", "N/A")))
        else:
            _warn("No cross-platform IDs returned")
    except requests.HTTPError as e:
        _fail("HTTP {}".format(e.response.status_code))

    track_ids = None
    if isrc:
        _info("Track IDs for ISRC {}...".format(isrc))
        try:
            track_ids = cm.get_track_ids_by_isrc(isrc)
            if track_ids:
                _ok("Found {} mapping(s)".format(len(track_ids)))
            else:
                _warn("No track mappings for this ISRC")
        except requests.HTTPError as e:
            _fail("HTTP {}".format(e.response.status_code))

    return {"artist_ids": artist_ids, "track_ids": track_ids}


def step_luminate(lum, isrc, label=""):
    """Step 4: Luminate consumption data by ISRC."""
    _header("STEP 4: Luminate -- Consumption Data  " + label)
    _info("ISRC: " + isrc)

    data = None
    try:
        data = lum.get_consumption_by_isrc(isrc)
    except Exception as e:
        _warn("Error: " + str(e))

    if data and data.get("title"):
        _ok("{} by {}".format(
            repr(data["title"]), data.get("display_artist_name", "?")))
        streams = lum.extract_stream_count(data)
        if streams:
            _kv("Total Streams", _num(streams))
        mlist = data.get("metrics", [])
        if mlist:
            _section("All Metrics")
            for m in mlist[:8]:
                name = m.get("metric_name") or m.get("name") or "?"
                _kv(name, _num(m.get("value", 0)))
        return data
    else:
        _warn("Luminate returned no data (service may be down)")
        _info("Revenue projections will use SoundCloud-based model.")
        return None


def step_revenue(sc_plays, track_title=""):
    """Step 5: Revenue projection and viability assessment."""
    _header("STEP 5: Revenue Projection")
    _info("SoundCloud plays: " + _num(sc_plays))
    if track_title:
        _info("Track: " + repr(track_title))

    proj = project_revenue(sc_plays)

    _section("Projected Revenue")
    fmt = "  {:<15} {:>18} {:>14} {:>14} {:>14}"
    print(fmt.format(
        "Tier", "Est. DSP Streams", "Spotify", "Apple Music", "All DSPs"))
    print("  " + "-" * 75)
    for tier, d in proj.items():
        r = d["revenue"]
        print(fmt.format(
            tier,
            _num(d["estimated_streams"]),
            _usd(r["spotify"]),
            _usd(r["apple_music"]),
            _usd(r["all_dsps_avg"]),
        ))

    viability = assess_viability(proj)
    _section("Viability Assessment")
    mid_s = "$" + _num(int(viability["mid_revenue"]))
    thr_s = "$" + _num(viability["threshold"])
    if viability["clears_threshold"]:
        _ok("CLEARS {} threshold (mid tier: {})".format(thr_s, mid_s))
    else:
        _warn("BELOW {} threshold (mid tier: {})".format(thr_s, mid_s))
    _info(viability["recommendation"])

    return {"projections": proj, "viability": viability}


def run(sc_url):
    """Run the complete Remix Radar pipeline from a SoundCloud URL."""
    sc = SoundCloudClient()
    cm = ChartmetricClient()
    lum = LuminateClient()

    _header("REMIX RADAR PIPELINE")
    _info("Input: " + sc_url)
    _info("Time:  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    passed = []
    failed = []

    sc_data = step_soundcloud(sc, sc_url)
    if not sc_data:
        failed.append("soundcloud")
        return {"passed": passed, "failed": failed}
    passed.append("soundcloud")

    parsed = sc_data["parsed"]
    artist_name = parsed["original_artist"]
    song_name = parsed["original_song"]
    if not artist_name:
        _warn("Could not parse original artist; using song title for search")
        artist_name = song_name

    cm_data = None
    if artist_name:
        cm_data = step_chartmetric_artist(cm, artist_name, song_name)
    if cm_data:
        passed.append("chartmetric_artist")
    else:
        failed.append("chartmetric_artist")

    isrc = None
    if cm_data:
        track_isrc = None
        if cm_data.get("track"):
            track_isrc = cm_data["track"].get("isrc")
        ids = step_chartmetric_ids(cm, cm_data["cm_id"], isrc=track_isrc)
        if ids.get("artist_ids"):
            passed.append("cross_platform_ids")
        else:
            failed.append("cross_platform_ids")
        if cm_data.get("track") and cm_data["track"].get("isrc"):
            isrc = cm_data["track"]["isrc"]

    lum_data = None
    if isrc:
        lum_label = "[" + repr(song_name or "") + "]"
        lum_data = step_luminate(lum, isrc, label=lum_label)
        if lum_data:
            passed.append("luminate")
        else:
            failed.append("luminate")
    else:
        _info("Skipping Luminate (no ISRC available)")
        failed.append("luminate_skipped")

    rev = step_revenue(
        sc_data["metrics"]["plays"],
        sc_data["track"]["title"],
    )
    passed.append("revenue_projection")

    _header("PIPELINE SUMMARY")
    total = len(passed) + len(failed)
    print("\n  Steps passed: {} / {}".format(len(passed), total))
    for s in passed:
        _ok(s)
    if failed:
        print("\n  Steps failed: {} / {}".format(len(failed), total))
        for s in failed:
            _fail(s)

    return {
        "passed": passed,
        "failed": failed,
        "soundcloud": sc_data,
        "chartmetric": cm_data,
        "luminate": lum_data,
        "revenue": rev,
    }


def main():
    print("=" * 64)
    print("  Remix Radar -- Pipeline")
    print("  Measure of Music 2026 Hackathon")
    print("=" * 64)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pyver = sys.version.split()[0]
    print("  Time:   " + now)
    print("  Python: " + pyver)

    _section("Credential Check")
    for name, ok in cfg.check_credentials():
        if ok:
            _ok(name)
        else:
            _fail(name)

    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = "https://soundcloud.com/revelriesmusic/blinding_lights"

    run(test_url)

    print("\n" + "=" * 64)
    print("  Done.")
    print("=" * 64)


if __name__ == "__main__":
    main()
