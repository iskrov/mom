"""
Chartmetric API Client for Remix Radar.

Chartmetric tracks 9M+ artists across streaming, social media, charts,
and radio. It is MANDATORY for the hackathon.

Rate limit: 4 requests/second (enforced via 0.3s delay between calls).

Usage:
    from scripts.platforms.chartmetric import ChartmetricClient

    cm = ChartmetricClient()
    artist = cm.find_artist("The Weeknd")
    geo = cm.get_where_people_listen(artist["id"])
    ids = cm.get_artist_platform_ids(artist["id"])
"""

import time

import requests

from scripts.config import cfg


class ChartmetricClient:
    """Client for the Chartmetric API (api.chartmetric.com)."""

    def __init__(self):
        self.base = cfg.CM_BASE

    def _get(self, path, params=None):
        """Authenticated GET with rate-limit throttling (0.3s between calls)."""
        token = cfg.cm_token()
        time.sleep(cfg.CM_RATE_LIMIT_DELAY)
        resp = requests.get(
            f"{self.base}{path}",
            headers={"Authorization": f"Bearer {token}"},
            params=params or {},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    # ── SEARCH ─────────────────────────────────────────────────────

    def search(self, query, entity_type="artists", limit=5):
        """
        Search across Chartmetric entities.

        Args:
            query:       Search string (name, keyword, or URL).
            entity_type: "artists", "tracks", "albums", "playlists",
                         "curators", "stations", "cities".
            limit:       Max results (default 5).

        Returns:
            List of matching objects. Artist objects include id, name,
            sp_followers, sp_monthly_listeners, cm_artist_score.
            Track objects include id, name, isrc, artist_names.
        """
        data = self._get("/search", {"q": query, "type": entity_type, "limit": limit})
        return data.get("obj", {}).get(entity_type, [])

    def find_artist(self, name, limit=5):
        """
        Smart artist search with automatic name-variant handling.

        Searches for the name plus common prefixes ("The", "DJ") and
        returns the best match ranked by cm_artist_score. Handles
        edge cases like "Weeknd" matching to "The Weeknd".

        Args:
            name:  Artist name (may be partial).
            limit: Results per search variant.

        Returns:
            Best-matching artist dict, or None.
        """
        variants = [name, f"The {name}", f"DJ {name}"]
        candidates = []
        for variant in variants:
            candidates.extend(self.search(variant, "artists", limit=limit))

        if not candidates:
            return None

        seen = set()
        unique = []
        for c in candidates:
            if c["id"] not in seen:
                seen.add(c["id"])
                unique.append(c)

        unique.sort(key=lambda a: a.get("cm_artist_score") or 0, reverse=True)
        return unique[0]

    # ── ARTISTS ────────────────────────────────────────────────────

    def get_artist(self, cm_id):
        """
        Full artist metadata by CM ID.

        Returns: name, cm_artist_rank, career_status, genres,
        record_label, hometown_city, code2, description, etc.

        NOTE: Spotify follower/listener counts come from the search
        result or get_artist_stats(), not this endpoint.
        """
        return self._get(f"/artist/{cm_id}").get("obj", {})

    def get_artist_career(self, cm_id):
        """
        Get artist career history snapshot for scoring.

        Returns Chartmetric career progression fields such as:
        - stage (undiscovered, developing, mid-level, mainstream, superstar, legendary)
        - stage_score (0-100)
        - momentum (decline, gradual decline, steady, growth, explosive growth)
        - momentum_score (0-100)
        """
        return self._get(f"/artist/{cm_id}/career").get("obj", {})

    def get_artist_stats(self, cm_id, platform, since=None, until=None):
        """
        Time-series fan/follower metrics for a platform.

        Args:
            cm_id:    Chartmetric artist ID.
            platform: "spotify", "soundcloud", "youtube_channel",
                      "instagram", "twitter", "tiktok", "deezer", etc.
            since/until: Date range (ISO strings).

        Returns: List of {value, timestp} dicts.
        """
        params = {}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return self._get(
            f"/artist/{cm_id}/stat/{platform}", params
        ).get("obj", [])

    def get_where_people_listen(self, cm_id, since=None):
        """
        Spotify "Where People Listen" geographic data.

        Returns city-level listener counts with affinity scores.
        Affinity > 1.0 = city over-indexes for this artist.

        Args:
            cm_id: Chartmetric artist ID.
            since: Start date (ISO string).

        Returns:
            Dict with "cities" and "countries" keys.
            cities: {CityName: [{listeners, code2, city_affinity, ...}]}
        """
        params = {"since": since} if since else {}
        return self._get(
            f"/artist/{cm_id}/where-people-listen", params
        ).get("obj", {})

    def get_artist_playlists(self, cm_id, platform="spotify",
                             status="current", limit=10):
        """Playlists currently or previously featuring the artist."""
        return self._get(
            f"/artist/{cm_id}/{platform}/{status}/playlists",
            {"limit": limit},
        ).get("obj", [])

    def get_related_artists(self, cm_id, limit=10):
        """Similar/related artists."""
        return self._get(
            f"/artist/{cm_id}/relatedartists", {"limit": limit}
        ).get("obj", [])

    def get_artist_platform_ids(self, cm_id):
        """
        Cross-platform IDs for an artist.

        CM -> Spotify, iTunes, Deezer, Amazon IDs.

        Returns list of dicts with: cm_artist, artist_name,
        spotify_artist_id, itunes_artist_id, deezer_artist_id,
        amazon_artist_id.
        """
        return self._get(
            f"/artist/chartmetric/{cm_id}/get-ids"
        ).get("obj", [])

    def get_artist_ids_by_spotify(self, spotify_id):
        """Look up CM + other IDs from a Spotify artist ID."""
        return self._get(
            f"/artist/spotify/{spotify_id}/get-ids"
        ).get("obj", [])

    # ── TRACKS ─────────────────────────────────────────────────────

    def get_track(self, cm_track_id):
        """
        Full track metadata by CM track ID.

        Returns: name, isrc, artist_names, spotify_track_ids,
        album_label, release_dates, tags, cm_statistics.
        """
        return self._get(f"/track/{cm_track_id}").get("obj", {})

    def get_track_stats(self, cm_track_id, platform,
                        since=None, until=None):
        """Time-series stats for a track on a specific platform."""
        params = {}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return self._get(
            f"/track/{cm_track_id}/{platform}/stats", params
        ).get("obj", [])

    def get_track_playlists(self, cm_track_id, platform="spotify",
                            status="current", limit=10):
        """Playlists containing a track."""
        return self._get(
            f"/track/{cm_track_id}/{platform}/{status}/playlists",
            {"limit": limit},
        ).get("obj", [])

    def get_track_platform_ids(self, cm_track_id):
        """Cross-platform IDs for a track by CM track ID."""
        return self._get(
            f"/track/chartmetric/{cm_track_id}/get-ids"
        ).get("obj", [])

    def get_track_ids_by_isrc(self, isrc):
        """
        Look up CM + other platform track IDs from an ISRC.

        Key bridge for verifying whether a remix exists on DSPs.
        """
        return self._get(
            f"/track/isrc/{isrc}/get-ids"
        ).get("obj", [])

    # ── CHARTS ─────────────────────────────────────────────────────

    def get_chart(self, platform, params=None):
        """
        Chart data for a platform.

        Args:
            platform: e.g., "spotify", "soundcloud", "shazam",
                      "applemusic/tracks", "beatport".
            params:   Additional query params (date, country, etc.).
        """
        return self._get(
            f"/charts/{platform}", params
        ).get("obj", [])

    # ── CITIES ─────────────────────────────────────────────────────

    def get_city_top_artists(self, city_id, source="spotify", limit=10):
        """Top artists in a city."""
        return self._get(
            f"/city/{city_id}/{source}/top-artists", {"limit": limit}
        ).get("obj", [])

    # ── HELPERS ────────────────────────────────────────────────────

    @staticmethod
    def parse_geo_data(geo_response):
        """
        Parse Where People Listen into a flat, sorted list.

        The raw response is {cities: {Name: [entries], ...}}.
        Returns [{name, code2, listeners, affinity}, ...] sorted
        by listener count descending.
        """
        cities = []
        raw = geo_response.get("cities", {})
        if isinstance(raw, dict):
            for city_name, entries in raw.items():
                if entries:
                    e = entries[0]
                    cities.append({
                        "name": city_name,
                        "code2": e.get("code2", ""),
                        "listeners": e.get("listeners", 0),
                        "affinity": e.get("city_affinity", 0),
                    })
        cities.sort(key=lambda c: c["listeners"], reverse=True)
        return cities
