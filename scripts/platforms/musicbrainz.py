"""MusicBrainz client for writer and publisher data lookup."""

import time

import musicbrainzngs

musicbrainzngs.set_useragent("RemixRadar", "0.1", "hello@remixradar.com")

_WRITER_TYPES = {"composer", "lyricist", "writer"}
_MB_RATE_DELAY = 1.1  # seconds — MusicBrainz allows 1 req/sec for anonymous clients


def get_work_parties(artist_name: str, song_title: str) -> list[dict]:
    """
    Look up writer and publisher data for a song via MusicBrainz.

    Flow:
      1. Search recordings by song title + artist name.
      2. Take the highest-scoring match (min score 60).
      3. Fetch recording with work-rels to get the composition work ID.
      4. Fetch the work with artist-rels (writers) and label-rels (publishers).
      5. Return party entries with estimated equal-split percentages:
           - Writers share 50% of the pool equally.
           - Publishers share the remaining 50% equally.
           - If no publishers are found, writers receive 100%.

    Returns an empty list if the song cannot be found or on any error.
    Share percentages are estimates only — exact splits are not available
    from MusicBrainz.
    """
    if not artist_name or not song_title:
        return []

    # Step 1: find the recording
    try:
        result = musicbrainzngs.search_recordings(
            recording=song_title,
            artist=artist_name,
            limit=3,
        )
    except Exception:
        return []

    recordings = result.get("recording-list", [])
    if not recordings:
        return []

    best = max(recordings, key=lambda r: int(r.get("ext:score", 0)), default=None)
    if not best or int(best.get("ext:score", 0)) < 60:
        return []

    rec_id = best.get("id")
    if not rec_id:
        return []

    # Step 2: get releases (for label data) and work relationships
    time.sleep(_MB_RATE_DELAY)
    try:
        rec_detail = musicbrainzngs.get_recording_by_id(rec_id, includes=["releases", "work-rels"])
    except Exception:
        return []

    recording_data = rec_detail.get("recording", {})

    # Collect label/master-rights entries from the release list
    seen_labels: set[str] = set()
    label_entries: list[dict] = []
    for release in recording_data.get("release-list", []):
        for label_info in release.get("label-info-list", []):
            label = label_info.get("label") or {}
            name = label.get("name", "")
            if name and name not in seen_labels:
                seen_labels.add(name)
                label_entries.append({
                    "party": name,
                    "publisher": name,
                    "role": "master rights",
                    "share_pct": 0.0,
                })

    work_rels = recording_data.get("work-relation-list", [])
    if not work_rels:
        # No composition data — return labels alone if we found any
        return label_entries

    # Prefer a "performance" relationship; fall back to the first work found
    work_id = None
    for rel in work_rels:
        if rel.get("type", "").lower() == "performance":
            work_id = (rel.get("work") or {}).get("id")
            break
    if not work_id:
        work_id = (work_rels[0].get("work") or {}).get("id")
    if not work_id:
        return label_entries

    # Step 3: get writers and publishers from the work
    time.sleep(_MB_RATE_DELAY)
    try:
        work_detail = musicbrainzngs.get_work_by_id(work_id, includes=["artist-rels", "label-rels"])
    except Exception:
        return []

    work = work_detail.get("work", {})

    writers = []
    for rel in work.get("artist-relation-list", []):
        if rel.get("type", "").lower() in _WRITER_TYPES:
            name = (rel.get("artist") or {}).get("name", "")
            if name:
                writers.append({"name": name, "role": rel["type"].lower()})

    publishers = []
    for rel in work.get("label-relation-list", []):
        if rel.get("type", "").lower() == "publisher":
            name = (rel.get("label") or {}).get("name", "")
            if name:
                publishers.append(name)

    if not writers:
        # No composition credits — return labels alone if we found any
        return label_entries

    # Step 4: build entries with estimated splits
    n_writers = len(writers)
    n_publishers = len(publishers)

    if n_publishers > 0:
        writer_pool = 50.0
        pub_pool = 50.0
    else:
        writer_pool = 100.0
        pub_pool = 0.0

    writer_share = round(writer_pool / n_writers, 1)
    pub_share = round(pub_pool / n_publishers, 1) if n_publishers > 0 else 0.0

    entries = []
    for i, w in enumerate(writers):
        # Absorb any rounding remainder into the last writer entry
        if i == n_writers - 1:
            allocated = writer_share * (n_writers - 1) + pub_share * n_publishers
            share = round(100.0 - allocated, 1)
        else:
            share = writer_share
        entries.append({
            "party": w["name"],
            "publisher": publishers[0] if publishers else "Independent",
            "role": w["role"],
            "share_pct": share,
        })

    for pub_name in publishers:
        entries.append({
            "party": pub_name,
            "publisher": pub_name,
            "role": "publisher",
            "share_pct": pub_share,
        })

    return entries + label_entries
