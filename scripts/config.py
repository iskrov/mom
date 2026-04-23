"""
Shared configuration and authentication for Remix Radar.

Loads API credentials from the .env file and provides centralized
token management so that platform clients never deal with auth
mechanics directly.

Usage:
    from scripts.config import cfg

    cfg.cm_token()    # -> valid Chartmetric bearer token (auto-refreshes)
    cfg.lum_token()   # -> valid Luminate bearer token (auto-refreshes)
    cfg.SC_CLIENT_ID  # -> SoundCloud public client_id
"""

import logging
import os
import re
import time

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def _fetch_sc_client_id():
    """Extract a fresh client_id from SoundCloud's JS bundle."""
    try:
        html = requests.get(
            "https://soundcloud.com",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        ).text
        scripts = re.findall(r'src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"', html)
        for url in scripts[-3:]:
            js = requests.get(url, timeout=10).text
            match = re.search(r'client_id\s*:\s*"([a-zA-Z0-9]{32})"', js)
            if match:
                logger.info("Fetched fresh SoundCloud client_id from JS bundle")
                return match.group(1)
    except Exception as exc:
        logger.warning("Could not auto-fetch SoundCloud client_id: %s", exc)
    return None

# ── Load .env ──────────────────────────────────────────────────────

_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(_env_path)


class _Config:
    """
    Singleton-style config holder.

    All API credentials and base URLs live here so that platform
    modules import one object and never touch os.environ directly.
    """

    # ── SoundCloud (unofficial v2 API) ─────────────────────────────

    SC_CLIENT_ID = os.getenv("SOUNDCLOUD_CLIENT_ID", "b73paRnaV82c1ypnjCCsgrFwg47vYs8a")
    SC_BASE = "https://api-v2.soundcloud.com"

    # SoundCloud's api-v2 rejects requests without browser-like headers.
    SC_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        ),
        "Referer": "https://soundcloud.com/",
        "Origin": "https://soundcloud.com",
    }

    # ── Chartmetric ────────────────────────────────────────────────

    CM_BASE = "https://api.chartmetric.com/api"
    CM_REFRESH_TOKEN = os.getenv("CHARTMETRIC_REFRESH_TOKEN")
    CM_RATE_LIMIT_DELAY = 0.3  # seconds between requests (4 req/sec limit)

    # ── Luminate ───────────────────────────────────────────────────

    LUM_BASE = "https://api.luminatedata.com"
    LUM_API_KEY = os.getenv("LUMINATE_API_KEY")
    LUM_EMAIL = os.getenv("LUMINATE_EMAIL")
    LUM_PASSWORD = os.getenv("LUMINATE_PASSWORD")

    # ── Revenue model constants ────────────────────────────────────

    STREAM_RATES = {
        "spotify": 0.004,
        "apple_music": 0.007,
        "all_dsps_avg": 0.005,
    }

    PROJECTION_TIERS = {
        "conservative": 1.0,
        "mid": 3.0,
        "optimistic": 5.0,
    }

    VIABILITY_THRESHOLD = 50_000  # USD — minimum mid-tier revenue to recommend clearance

    # ── Internal token cache ───────────────────────────────────────

    def __init__(self):
        self._tokens = {}
        if not os.getenv("SOUNDCLOUD_CLIENT_ID"):
            fetched = _fetch_sc_client_id()
            if fetched:
                self.SC_CLIENT_ID = fetched
        logger.warning("SoundCloud client_id in use: %s", self.SC_CLIENT_ID)
        # Verify the key works
        try:
            resp = requests.get(
                "https://api-v2.soundcloud.com/search/tracks",
                params={"q": "test", "limit": 1, "client_id": self.SC_CLIENT_ID},
                headers=self.SC_HEADERS,
                timeout=10,
            )
            logger.warning("SoundCloud key check: HTTP %s", resp.status_code)
        except Exception as exc:
            logger.warning("SoundCloud key check failed: %s", exc)

    # ── Chartmetric auth ───────────────────────────────────────────

    def cm_token(self):
        """
        Get a valid Chartmetric access token.

        The token lasts 1 hour. We cache it and re-fetch after 50 minutes.
        """
        cached = self._tokens.get("cm")
        if cached and (time.time() - cached["ts"]) < 3000:
            return cached["token"]

        resp = requests.post(
            f"{self.CM_BASE}/token",
            json={"refreshtoken": self.CM_REFRESH_TOKEN},
        )
        resp.raise_for_status()
        token = resp.json()["token"]
        self._tokens["cm"] = {"token": token, "ts": time.time()}
        return token

    # ── Luminate auth ──────────────────────────────────────────────

    def lum_token(self):
        """
        Get a valid Luminate access token.

        The token lasts 24 hours. We cache it and re-use within that window.
        """
        cached = self._tokens.get("lum")
        if cached and (time.time() - cached["ts"]) < 80000:
            return cached["token"]

        resp = requests.post(
            f"{self.LUM_BASE}/auth",
            headers={
                "x-api-key": self.LUM_API_KEY,
                "content-type": "application/x-www-form-urlencoded",
                "accept": "application/json",
            },
            data=f"username={self.LUM_EMAIL}&password={self.LUM_PASSWORD}",
        )
        resp.raise_for_status()
        body = resp.json()
        token = body.get("access_token") or body.get("token")
        self._tokens["lum"] = {"token": token, "ts": time.time()}
        return token

    # ── Credential validation ──────────────────────────────────────

    def check_credentials(self):
        """
        Verify that all required credentials are loaded.

        Returns a list of (name, is_ok) tuples.
        """
        checks = [
            ("CHARTMETRIC_REFRESH_TOKEN", bool(self.CM_REFRESH_TOKEN)),
            ("LUMINATE_API_KEY", bool(self.LUM_API_KEY)),
            ("LUMINATE_EMAIL", bool(self.LUM_EMAIL)),
            ("LUMINATE_PASSWORD", bool(self.LUM_PASSWORD)),
            ("SOUNDCLOUD_CLIENT_ID", bool(self.SC_CLIENT_ID)),
        ]
        return checks


# Module-level singleton — import this everywhere
cfg = _Config()
