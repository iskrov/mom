"""Pydantic request/response schemas for RemixRadar MVP API."""

from pydantic import BaseModel, Field


class ArtistSearchRequest(BaseModel):
    """Payload for artist-first remix discovery search."""

    artist_name: str = Field(min_length=1, description="Original artist name.")
    tracks_to_fetch: int = Field(default=10, ge=10, le=100)
    sort_by: str = Field(default="heat_score")
    sort_desc: bool = Field(default=True)
    genre_filter: list[str] = Field(default_factory=list)
    region: str = Field(default="Global")
    career_stages: list[str] = Field(default_factory=list)
    min_account_reach: int = Field(default=0, ge=0)
    max_account_reach: int = Field(default=500_000, ge=0)
    min_heat_score: float = Field(default=0.0, ge=0.0, le=10.0)
    max_heat_score: float = Field(default=10.0, ge=0.0, le=10.0)
    enrich_chartmetric: bool = Field(default=True)
    check_official_release: bool = Field(default=False)


class SongSearchRequest(BaseModel):
    """Payload for song remix search."""

    song_name: str = Field(min_length=1)
    artist_name: str | None = None
    tracks_to_fetch: int = Field(default=10, ge=10, le=100)
    enrich_chartmetric: bool = Field(default=True)
    check_official_release: bool = Field(default=False)


class AnalyzeUrlRequest(BaseModel):
    """Payload for single-track analyze endpoint."""

    sc_url: str = Field(min_length=8)


class LicensingResponse(BaseModel):
    """Mock licensing split payload."""

    track_id: int
    split_set: str
    updated_at: str
    entries: list[dict]


class TrackDetailRequest(BaseModel):
    """Payload for optional explicit track detail analysis endpoint."""

    sc_url: str = Field(min_length=8)
