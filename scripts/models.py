"""
Remix Radar -- Business Logic Models.

Contains the remix title parser and revenue projection model.
These are the domain-specific logic components that sit between
the raw API data and the final pipeline output.
"""

import re
import math

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


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def _log_score(value, floor_value=1_000, cap_value=100_000_000):
    """Convert wide-range counts to a stable 0-100 score."""
    value = max(float(value or 0.0), 0.0)
    if value <= 0:
        return 0.0
    value = min(value, float(cap_value))
    num = math.log10(max(value, floor_value)) - math.log10(floor_value)
    den = math.log10(cap_value) - math.log10(floor_value)
    if den <= 0:
        return 0.0
    return _clamp((num / den) * 100.0)


def _ratio_score(value):
    """Map followers/listeners style ratio to 0-100."""
    value = float(value or 0.0)
    if value <= 0:
        return 0.0
    if value >= 0.20:
        return 100.0
    return _clamp((value / 0.20) * 100.0)


def _engagement_score(engagement_rate):
    """Map likes/plays to 0-100 where ~3% is exceptional."""
    rate = float(engagement_rate or 0.0)
    return _clamp((rate / 0.03) * 100.0)


def _momentum_category_score(momentum):
    mapping = {
        "decline": 15,
        "gradual decline": 30,
        "steady": 45,
        "growth": 70,
        "explosive growth": 95,
    }
    return float(mapping.get((momentum or "").strip().lower(), 45))


def _stage_rank(stage):
    mapping = {
        "undiscovered": 0,
        "developing": 1,
        "mid-level": 2,
        "mainstream": 3,
        "superstar": 4,
        "legendary": 5,
    }
    return mapping.get((stage or "").strip().lower(), 0)


def compute_geo_divergence(cities_a, cities_b, top_n=10):
    """
    Compute geographic divergence as Jaccard distance in [0, 1].

    0.0 -> identical city sets, 1.0 -> no overlap.
    """
    set_a = {c.get("name") for c in (cities_a or [])[:top_n] if c.get("name")}
    set_b = {c.get("name") for c in (cities_b or [])[:top_n] if c.get("name")}
    if not set_a and not set_b:
        return 0.0
    union = set_a.union(set_b)
    if not union:
        return 0.0
    inter = set_a.intersection(set_b)
    return _clamp((1.0 - (len(inter) / len(union))) * 100.0) / 100.0


def compute_demand_score(sc_metrics):
    """Demand score from SoundCloud engagement signals."""
    plays_score = _log_score(sc_metrics.get("plays"), floor_value=10_000, cap_value=10_000_000)
    engagement_score = _engagement_score(sc_metrics.get("engagement_rate"))
    velocity_score = _log_score(sc_metrics.get("daily_velocity"), floor_value=100, cap_value=20_000)

    comments = sc_metrics.get("comments") or 0
    reposts = sc_metrics.get("reposts") or 0
    bonus = 0.0
    if comments > 100:
        bonus += 5.0
    if reposts > 50:
        bonus += 5.0

    score = (plays_score * 0.40) + (engagement_score * 0.30) + (velocity_score * 0.30) + bonus
    return _clamp(score)


def compute_conversion_score(original_artist, remix_artist, original_geo, remix_geo):
    """Conversion score from DSP-readiness and market crossover signals."""
    original_listeners_score = _log_score(
        original_artist.get("sp_monthly_listeners"), floor_value=10_000, cap_value=100_000_000
    )
    remix_listeners_score = _log_score(
        remix_artist.get("sp_monthly_listeners"), floor_value=1_000, cap_value=20_000_000
    )
    loyalty_score = _ratio_score(remix_artist.get("spotify_followers_to_listeners_ratio"))
    geo_divergence_score = compute_geo_divergence(original_geo, remix_geo) * 100.0
    tiktok_score = _log_score(remix_artist.get("tiktok_followers"), floor_value=1_000, cap_value=10_000_000)

    score = (
        (original_listeners_score * 0.30)
        + (remix_listeners_score * 0.25)
        + (loyalty_score * 0.15)
        + (geo_divergence_score * 0.15)
        + (tiktok_score * 0.15)
    )
    return _clamp(score)


def compute_momentum_score(original_career, remix_career):
    """Momentum score from artist trajectory and stage-gap discovery bonus."""
    remix_momentum_cat = _momentum_category_score(remix_career.get("momentum"))
    remix_momentum_raw = float(remix_career.get("momentum_score") or 50.0)
    remix_momentum = (remix_momentum_cat * 0.6) + (remix_momentum_raw * 0.4)

    gap = _stage_rank(original_career.get("stage")) - _stage_rank(remix_career.get("stage"))
    stage_bonus = 0.0
    if gap >= 3:
        stage_bonus = 20.0
    elif gap == 2:
        stage_bonus = 10.0
    elif gap == 1:
        stage_bonus = 5.0

    penalty = 0.0
    remix_stage = (remix_career.get("stage") or "").strip().lower()
    remix_momentum_label = (remix_career.get("momentum") or "").strip().lower()
    if remix_stage == "mid-level" and remix_momentum_label in {"steady", "decline", "gradual decline"}:
        penalty = 15.0

    return _clamp(remix_momentum + stage_bonus - penalty)


def compute_opportunity_score(demand, conversion, momentum):
    """
    Compose overall Opportunity Score and decision label.

    Formula:
        overall = demand*0.40 + conversion*0.35 + momentum*0.25
    """
    overall = _clamp((demand * 0.40) + (conversion * 0.35) + (momentum * 0.25))
    if overall >= 80:
        label = "STRONG"
    elif overall >= 60:
        label = "MODERATE"
    elif overall >= 40:
        label = "MARGINAL"
    else:
        label = "WEAK"

    return {
        "overall": round(overall, 1),
        "label": label,
        "demand": round(demand, 1),
        "conversion": round(conversion, 1),
        "momentum": round(momentum, 1),
    }


def build_opportunity_score(sc_metrics, original_artist, remix_artist, original_geo, remix_geo, original_career, remix_career):
    """Convenience wrapper to compute full score payload in one call."""
    demand = compute_demand_score(sc_metrics)
    conversion = compute_conversion_score(original_artist, remix_artist, original_geo, remix_geo)
    momentum = compute_momentum_score(original_career, remix_career)
    return compute_opportunity_score(demand, conversion, momentum)
