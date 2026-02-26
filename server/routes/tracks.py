"""Track-centric routes for RemixRadar MVP API."""

from datetime import datetime, timezone

from fastapi import APIRouter

from scripts.pipeline import analyze_track_object, make_clients
from scripts.platforms.musicbrainz import get_work_parties

from server.schemas import LicensingResponse, TrackDetailRequest

router = APIRouter(prefix="/api/tracks", tags=["tracks"])


def _fallback_entries() -> list[dict]:
    """Minimal placeholder returned when MusicBrainz has no data."""
    return [
        {
            "party": "Rights Holder",
            "publisher": "Unknown",
            "role": "writer",
            "share_pct": 100.0,
        }
    ]


@router.get("/{track_id}/licensing", response_model=LicensingResponse)
def get_licensing(track_id: int, song_title: str = "", artist_name: str = ""):
    """
    Return writer and publisher data for the original song via MusicBrainz.

    Accepts song_title and artist_name as optional query parameters.
    Falls back to a placeholder entry if MusicBrainz returns no results.
    Split percentages are estimated (equal splits across writers/publishers).
    """
    if song_title and artist_name:
        entries = get_work_parties(artist_name=artist_name, song_title=song_title)
    else:
        entries = []

    if not entries:
        entries = _fallback_entries()
        split_set = "Placeholder — provide song_title and artist_name for real data"
    elif all(e.get("role") == "master rights" for e in entries):
        split_set = "MusicBrainz · label data only"
    else:
        split_set = "MusicBrainz · estimated splits"

    return LicensingResponse(
        track_id=track_id,
        split_set=split_set,
        updated_at=datetime.now(timezone.utc).isoformat(),
        entries=entries,
    )


@router.post("/detail")
def get_track_detail(payload: TrackDetailRequest):
    """
    Optional detail endpoint for compatibility with prior planning.

    The frontend can skip this and rely on SSE payloads; this route
    remains available for direct detail retrieval by SoundCloud URL.
    """
    clients = make_clients()
    sc_track = clients["sc"].resolve(payload.sc_url)
    return analyze_track_object(sc_track, clients)
