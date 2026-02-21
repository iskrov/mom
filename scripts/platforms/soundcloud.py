"""
SoundCloud API Client for Remix Radar.

Uses the unofficial api-v2 endpoint with a public client_id extracted
from SoundCloud's web app. No OAuth credentials required for read-only
access to public tracks, users, and playlists.

IMPORTANT: This client_id is NOT an official credential and could stop
working at any time. If the hackathon provides official OAuth creds,
update SC_CLIENT_ID in config.py.

Usage:
    from scripts.platforms.soundcloud import SoundCloudClient

    sc = SoundCloudClient()
    track = sc.resolve("https://soundcloud.com/artist/track")
    metrics = sc.compute_metrics(track)
    remixes = sc.search_remixes("Blinding Lights", artist="The Weeknd")
"""

from datetime import datetime

import requests

from scripts.config import cfg


class SoundCloudClient:
    """Client for SoundCloud's unofficial v2 API."""

    def __init__(self):
        self.base = cfg.SC_BASE
        self.client_id = cfg.SC_CLIENT_ID
        self.headers = cfg.SC_HEADERS

    def _get(self, path, params=None):
        """GET request with client_id and browser headers."""
        params = params or {}
        params["client_id"] = self.client_id
        resp = requests.get(
            f"{self.base}{path}",
            params=params,
            headers=self.headers,
        )
        resp.raise_for_status()
        return resp.json()

    # ── Core endpoints ─────────────────────────────────────────────

    def resolve(self, url):
        """
        Resolve a SoundCloud permalink URL to its full API resource.

        Args:
            url: Full SoundCloud URL, e.g.
                 "https://soundcloud.com/revelriesmusic/blinding_lights"

        Returns:
            Track (or User/Playlist) object with all metadata fields.

        Raises:
            requests.HTTPError: if URL is invalid or track not found.
        """
        return self._get("/resolve", {"url": url})

    def get_track(self, track_id):
        """
        Get a track by its numeric SoundCloud ID.

        Args:
            track_id: Integer track ID (e.g., 851514058).

        Returns:
            Full track object.
        """
        return self._get(f"/tracks/{track_id}")

    def search_tracks(self, query, limit=50, genre=None, created_after=None):
        """
        Search for tracks by keyword.

        The query matches against title, username, and description.

        Args:
            query:         Search string (e.g., "blinding lights remix").
            limit:         Max results per page (1-200, default 50).
            genre:         Optional genre filter (e.g., "Deep House").
            created_after: Optional ISO date string — only tracks uploaded
                           after this date (e.g., "2024-01-01").

        Returns:
            List of track objects.
        """
        params = {"q": query, "limit": limit}
        if genre:
            params["genres"] = genre
        if created_after:
            params["created_at[from]"] = created_after
        data = self._get("/search/tracks", params)
        return data.get("collection", [])

    def search_remixes(self, song_name, artist=None, limit=50):
        """
        Search for remixes of a specific song.

        Constructs a search query like "Blinding Lights remix" and
        optionally filters results whose titles contain the artist name.

        Args:
            song_name: Original song title.
            artist:    Optional original artist name for filtering.
            limit:     Max results (default 50).

        Returns:
            List of track objects, sorted by playback_count descending.
        """
        query = f"{song_name} remix"
        results = self.search_tracks(query, limit=limit)

        if artist:
            artist_lower = artist.lower()
            results = [
                t for t in results
                if artist_lower in t.get("title", "").lower()
                or artist_lower in (t.get("user", {}).get("username", "")).lower()
                or artist_lower in (t.get("description") or "").lower()
            ]

        results.sort(key=lambda t: t.get("playback_count") or 0, reverse=True)
        return results

    def get_related(self, track_id, limit=50):
        """
        Get tracks related to a given track.

        Useful for discovering other remixes of the same song.

        Args:
            track_id: Integer track ID.
            limit:    Max results.

        Returns:
            List of related track objects.
        """
        data = self._get(f"/tracks/{track_id}/related", {"limit": limit})
        return data.get("collection", [])

    def get_comments(self, track_id, limit=200):
        """
        Get comments on a track.

        Comment sentiment and volume can be an engagement signal.

        Args:
            track_id: Integer track ID.
            limit:    Max results.

        Returns:
            List of comment objects.
        """
        data = self._get(f"/tracks/{track_id}/comments", {"limit": limit})
        return data.get("collection", [])

    def get_user(self, user_id):
        """
        Get a user profile by ID.

        Args:
            user_id: Integer user ID.

        Returns:
            User object with followers_count, track_count, etc.
        """
        return self._get(f"/users/{user_id}")

    def get_user_tracks(self, user_id, limit=50):
        """
        Get all public tracks by a user.

        Args:
            user_id: Integer user ID.
            limit:   Max results.

        Returns:
            List of track objects.
        """
        data = self._get(f"/users/{user_id}/tracks", {"limit": limit})
        return data.get("collection", [])

    # ── Derived metrics ────────────────────────────────────────────

    @staticmethod
    def compute_metrics(track):
        """
        Compute derived engagement metrics from a track object.

        Args:
            track: A SoundCloud track object (from resolve, search, etc.).

        Returns:
            Dict with:
                plays            — total play count
                likes            — total likes
                reposts          — total reposts
                comments         — total comments
                engagement_rate  — likes / plays
                daily_velocity   — plays per day since upload
                days_live        — days since upload
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

    @staticmethod
    def extract_isrc(track):
        """
        Extract ISRC from a track's publisher_metadata, if present.

        Not all tracks have this — it depends on whether the uploader
        filled in the ISRC field. When present, this is the ISRC of
        the uploaded track (i.e., the remix), not the original song.

        Args:
            track: A SoundCloud track object.

        Returns:
            ISRC string, or None.
        """
        meta = track.get("publisher_metadata") or {}
        return meta.get("isrc")
