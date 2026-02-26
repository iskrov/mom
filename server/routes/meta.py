"""Metadata routes to drive UI labels/options from backend."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/ui")
def get_ui_metadata():
    """Return workflow/tab/filter seed metadata for frontend rendering."""
    return {
        "organization": "Warner Music Group",
        "default_mode": "artist_search",
        "tabs": [
            {"group": "RIGHTSHOLDER", "label": "Catalog Search", "key": "catalog_search", "active": False},
            {"group": "RIGHTSHOLDER", "label": "Artist Search", "key": "artist_search", "active": True},
            {"group": "RIGHTSHOLDER", "label": "Song Search", "key": "song_search", "active": False},
            {"group": "DISCOVERY", "label": "Remix Browse", "key": "remix_browse", "active": False},
            {"group": "DISCOVERY", "label": "SC Link Lookup", "key": "sc_link_lookup", "active": False},
        ],
        "filters": {
            "genres": ["All", "Pop", "Hip-Hop", "EDM", "R&B", "Latin", "Dance & EDM", "Synthwave"],
            "regions": ["Global"],
            "career_stages": ["Developing", "Mid-level", "Established"],
            "tracks_to_fetch": {"min": 1, "max": 20, "default": 10},
            "account_reach": {"min": 0, "max": 500000, "default_min": 0, "default_max": 500000},
            "heat_score": {"min": 0.0, "max": 10.0, "default_min": 0.0, "default_max": 10.0},
        },
        "placeholders": {
            "catalog_search": {
                "title": "Catalog Search is coming soon",
                "description": "Bulk CSV/XML upload flow will rank remix opportunities across your catalog.",
                "next_steps": [
                    "Upload parser integration from scripts/catalog.py",
                    "Batch SSE enrichment job orchestration",
                    "Progress + resumable processing UI",
                ],
            },
            "remix_browse": {
                "title": "Remix Browse is coming soon",
                "description": "Discovery mode for trending remix candidates by genre, region, and velocity.",
                "next_steps": [
                    "Discovery query presets and saved views",
                    "Top charts + trend-signal fusion",
                    "Review queue and assignment actions",
                ],
            },
        },
    }
