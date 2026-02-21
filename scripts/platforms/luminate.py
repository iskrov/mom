"""
Luminate API Client for Remix Radar.

Luminate provides industry-standard consumption data: streaming,
sales, airplay, and Billboard chart data across 63 territories.

Known issues:
  - search size param must be >= 10 or results silently return empty
  - Data endpoints may return HTTP 500 during service outages
"""

from datetime import datetime, timedelta

import requests

from scripts.config import cfg


class LuminateClient:
    """Client for the Luminate Music API."""

    def __init__(self):
        self.base = cfg.LUM_BASE

    def _headers(self):
        token = cfg.lum_token()
        return {
            "Authorization": f"Bearer {token}",
            "x-api-key": cfg.LUM_API_KEY,
            "Accept": "application/vnd.luminate-data.svc-apibff.v1+json",
        }

    def _get(self, path, params=None):
        resp = requests.get(
            f"{self.base}{path}",
            headers=self._headers(),
            params=params or {},
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _default_dates(start_date=None, end_date=None, days_back=90):
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (
                datetime.now() - timedelta(days=days_back)
            ).strftime("%Y-%m-%d")
        return start_date, end_date

    def search(self, query, entity_type="artist", size=10):
        """Search Luminate. size must be >= 10."""
        return self._get("/search", {
            "query": query,
            "entity_type": entity_type,
            "size": max(size, 10),
        }).get("results", [])

    def get_song_by_isrc(self, isrc, location="US",
                         start_date=None, end_date=None):
        """Song-level consumption data by ISRC."""
        start_date, end_date = self._default_dates(start_date, end_date)
        return self._get(f"/songs/{isrc}", {
            "id_type": "isrc", "metrics": "all",
            "location": location,
            "start_date": start_date, "end_date": end_date,
            "metadata_level": "max",
        })

    def get_recording_by_isrc(self, isrc, location="US",
                              start_date=None, end_date=None):
        """Recording-level consumption data by ISRC."""
        start_date, end_date = self._default_dates(start_date, end_date)
        return self._get(f"/musical_recordings/{isrc}", {
            "id_type": "isrc", "metrics": "all",
            "location": location,
            "start_date": start_date, "end_date": end_date,
            "metadata_level": "max",
        })

    def get_consumption_by_isrc(self, isrc, location="US",
                                start_date=None, end_date=None):
        """Try /songs/ then /musical_recordings/. Returns None if both fail."""
        try:
            data = self.get_song_by_isrc(isrc, location, start_date, end_date)
            if data.get("title"):
                return data
        except requests.HTTPError:
            pass
        try:
            data = self.get_recording_by_isrc(
                isrc, location, start_date, end_date
            )
            if data.get("title"):
                return data
        except requests.HTTPError:
            pass
        return None

    def get_artist(self, luminate_id, location="US",
                   start_date=None, end_date=None, metrics="all"):
        """Artist metadata and consumption data."""
        start_date, end_date = self._default_dates(start_date, end_date)
        return self._get(f"/artists/{luminate_id}", {
            "metrics": metrics, "location": location,
            "start_date": start_date, "end_date": end_date,
        })

    def list_charts(self):
        """List all available charts."""
        return self._get("/charts")

    def get_chart(self, chart_id, week=None):
        """Chart rankings for a specific week (YYYY-Www format)."""
        params = {"chart_week": week} if week else {}
        return self._get(f"/charts/{chart_id}", params)

    @staticmethod
    def extract_stream_count(data):
        """Extract total stream count from a Luminate response."""
        for m in data.get("metrics", []):
            name = (m.get("metric_name") or m.get("name") or "").lower()
            if "stream" in name and "total" in name:
                return m.get("value")
        for m in data.get("metrics", []):
            name = (m.get("metric_name") or m.get("name") or "").lower()
            if "stream" in name:
                return m.get("value")
        return None
