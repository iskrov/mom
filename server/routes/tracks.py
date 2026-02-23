"""Track-centric routes for RemixRadar MVP API."""

from datetime import datetime, timezone

from fastapi import APIRouter

from scripts.pipeline import analyze_track_object, make_clients

from server.schemas import LicensingResponse, TrackDetailRequest

router = APIRouter(prefix="/api/tracks", tags=["tracks"])


def _mock_split_entries(track_id: int) -> list[dict]:
    """Return deterministic mock licensing entries for a track."""
    base = [
        ("Primary Rights Holder", "Sony Pub", "co-writer", 32.5),
        ("Original Artist", "Warner Chappell", "artist", 22.5),
        ("Remix Artist", "Independent", "remixer", 20.0),
        ("Producer", "UMG", "producer", 15.0),
        ("Co-Writer", "BMI", "co-writer", 10.0),
    ]
    # Light deterministic shuffle by track id.
    offset = track_id % len(base)
    rotated = base[offset:] + base[:offset]
    return [
        {
            "party": row[0],
            "publisher": row[1],
            "role": row[2],
            "share_pct": row[3],
        }
        for row in rotated
    ]


@router.get("/{track_id}/licensing", response_model=LicensingResponse)
def get_licensing(track_id: int):
    """Mock licensing response placeholder for later Royalti integration."""
    return LicensingResponse(
        track_id=track_id,
        split_set="Mock split v1",
        updated_at=datetime.now(timezone.utc).isoformat(),
        entries=_mock_split_entries(track_id),
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
