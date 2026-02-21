"""
Remix Radar -- Business Logic Models.

Contains the remix title parser and revenue projection model.
These are the domain-specific logic components that sit between
the raw API data and the final pipeline output.
"""

import re

from scripts.config import cfg


_REMIX_PAREN = re.compile(
    r"\s*\(([^)]+?)\s+(?:remix|edit|bootleg|flip|rework|vip|mix)\)",
    re.IGNORECASE,
)

_REMIX_BRACKET = re.compile(
    r"\s*\[([^\]]+?)\s+(?:remix|edit|bootleg|flip|rework|vip|mix)\]",
    re.IGNORECASE,
)

_COVER_RE = re.compile(r"cover", re.IGNORECASE)
_COVER_STRIP = re.compile(r"\s+cover.*$", re.IGNORECASE)
_TRAILING_REMIX = re.compile(r"\s*[-\u2013]\s*(?:remix|edit|bootleg|flip|rework)$", re.IGNORECASE)


def parse_remix_title(title):
    """Extract original artist, song, and remix artist from a SoundCloud title.

    Handles patterns like 'Artist - Song (RemixArtist Remix)' and cover
    patterns like 'Revelries - Blinding Lights (Weeknd Cover Remix)'.

    Returns dict with original_artist, original_song, remix_artist, raw_title.
    """
    result = {
        "original_artist": None,
        "original_song": None,
        "remix_artist": None,
        "raw_title": title,
    }

    match = _REMIX_PAREN.search(title) or _REMIX_BRACKET.search(title)
    is_cover = False

    if match:
        inner = match.group(1).strip()
        if _COVER_RE.search(inner):
            is_cover = True
            cover_name = _COVER_STRIP.sub("", inner).strip()
            if cover_name:
                result["original_artist"] = cover_name
        else:
            result["remix_artist"] = inner

    clean = _REMIX_PAREN.sub("", title)
    clean = _REMIX_BRACKET.sub("", clean).strip()
    clean = _TRAILING_REMIX.sub("", clean).strip()

    for sep in (" - ", " \u2013 ", " \u2014 "):
        if sep in clean:
            parts = clean.split(sep, 1)
            if is_cover:
                result["remix_artist"] = parts[0].strip()
            else:
                result["original_artist"] = parts[0].strip()
            result["original_song"] = parts[1].strip()
            return result

    result["original_song"] = clean
    return result


def project_revenue(sc_plays):
    """3-tier revenue projections from SoundCloud play count.

    Returns dict keyed by tier (conservative/mid/optimistic) with
    estimated_streams and revenue by platform.
    """
    result = {}
    for tier, mult in cfg.PROJECTION_TIERS.items():
        streams = int(sc_plays * mult)
        result[tier] = {
            "estimated_streams": streams,
            "revenue": {
                p: round(streams * r, 2)
                for p, r in cfg.STREAM_RATES.items()
            },
        }
    return result


def assess_viability(projections):
    """Check if a remix clears the viability threshold.

    Uses mid-tier 'all_dsps_avg' revenue vs the configured threshold.
    """
    mid_rev = projections["mid"]["revenue"]["all_dsps_avg"]
    clears = mid_rev >= cfg.VIABILITY_THRESHOLD

    if clears:
        rec = "This remix warrants clearance evaluation."
    else:
        rec = "May not justify clearance costs at current engagement."

    return {
        "clears_threshold": clears,
        "mid_revenue": mid_rev,
        "threshold": cfg.VIABILITY_THRESHOLD,
        "recommendation": rec,
    }
