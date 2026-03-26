"""Discogs API client for fetching collection and release data.

Uses httpx.AsyncClient for HTTP calls with rate limiting via aiolimiter.
Auth via personal access token from settings. The token value is never logged.
"""

import logging
from typing import Annotated

import httpx
from aiolimiter import AsyncLimiter
from fastapi import Depends
from pydantic import BaseModel, ConfigDict

from cue_the_music.config import Settings, get_settings

logger = logging.getLogger(__name__)

# Lazy rate limiter: created on first use within the running event loop
# to avoid reuse across loops (which causes warnings in tests).
_rate_limiter: AsyncLimiter | None = None


def _get_rate_limiter() -> AsyncLimiter:
    """Return the shared rate limiter, creating it on first use."""
    global _rate_limiter  # noqa: PLW0603
    if _rate_limiter is None:
        # 1 request per 1.2s ≈ 50 req/min, no burst — Discogs rejects bursts
        _rate_limiter = AsyncLimiter(max_rate=1, time_period=1.2)
    return _rate_limiter

_USER_AGENT = "CueTheMusic/1.0"
_BASE_URL = "https://api.discogs.com"


# --- Pydantic models for Discogs API response validation ---


class DiscogsArtist(BaseModel):
    """An artist entry from the Discogs API response."""

    model_config = ConfigDict(extra="ignore")

    name: str


class DiscogsLabel(BaseModel):
    """A label entry from the Discogs API response."""

    model_config = ConfigDict(extra="ignore")

    name: str


class DiscogsBasicInformation(BaseModel):
    """The basic_information block from a Discogs collection release."""

    model_config = ConfigDict(extra="ignore")

    artists: list[DiscogsArtist]
    cover_image: str = ""
    genres: list[str] = []
    id: int
    labels: list[DiscogsLabel] = []
    master_id: int = 0
    styles: list[str] = []
    thumb: str = ""
    title: str
    year: int = 0


class DiscogsCollectionRelease(BaseModel):
    """A single release entry from the Discogs collection endpoint."""

    model_config = ConfigDict(extra="ignore")

    basic_information: DiscogsBasicInformation


class DiscogsPagination(BaseModel):
    """Pagination info from Discogs API responses."""

    model_config = ConfigDict(extra="ignore")

    page: int
    pages: int
    per_page: int


class DiscogsCollectionResponse(BaseModel):
    """Full response from the Discogs collection endpoint."""

    model_config = ConfigDict(extra="ignore")

    pagination: DiscogsPagination
    releases: list[DiscogsCollectionRelease]


class DiscogsTrack(BaseModel):
    """A single track from a Discogs release detail response."""

    model_config = ConfigDict(extra="ignore")

    duration: str = ""
    position: str = ""
    title: str = ""
    type_: str = ""


class DiscogsReleaseDetail(BaseModel):
    """Relevant fields from the Discogs release detail endpoint."""

    model_config = ConfigDict(extra="ignore")

    id: int
    tracklist: list[DiscogsTrack] = []


class DiscogsMasterRelease(BaseModel):
    """Relevant fields from the Discogs master release endpoint."""

    model_config = ConfigDict(extra="ignore")

    id: int
    tracklist: list[DiscogsTrack] = []
    year: int = 0


# --- Client ---


class DiscogsClient:
    """HTTP client for the Discogs API with rate limiting.

    Authenticates via a personal access token. All requests share a global
    rate limiter capped at 50 req/min to stay within Discogs' 60 req/min
    limit for authenticated users.
    """

    def __init__(self, settings: Settings) -> None:
        self._token = settings.DISCOGS_TOKEN
        self._username = settings.DISCOGS_USERNAME
        self._headers = {
            "Authorization": f"Discogs token={self._token}",
            "User-Agent": _USER_AGENT,
        }

    async def get_collection_page(
        self, username: str, page: int = 1
    ) -> DiscogsCollectionResponse:
        """Fetch one page of a user's Discogs collection.

        Args:
            username: Discogs username whose collection to fetch.
            page: Page number (1-indexed).

        Returns:
            Validated collection response with pagination and releases.
        """
        async with _get_rate_limiter():
            url = (
                f"{_BASE_URL}/users/{username}"
                f"/collection/folders/0/releases"
            )
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._headers,
                    params={"page": page, "per_page": 100},
                    timeout=30.0,
                )
                response.raise_for_status()
                return DiscogsCollectionResponse.model_validate(
                    response.json()
                )

    async def get_master_release(
        self, master_id: int
    ) -> DiscogsMasterRelease:
        """Fetch a master release to obtain the original release year.

        Args:
            master_id: Discogs master release ID.

        Returns:
            Validated master release with the original year.
        """
        async with _get_rate_limiter():
            url = f"{_BASE_URL}/masters/{master_id}"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return DiscogsMasterRelease.model_validate(response.json())

    async def get_release_detail(
        self, release_id: int
    ) -> DiscogsReleaseDetail:
        """Fetch release detail including tracklist.

        Args:
            release_id: Discogs release ID.

        Returns:
            Validated release detail with tracklist.
        """
        async with _get_rate_limiter():
            url = f"{_BASE_URL}/releases/{release_id}"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return DiscogsReleaseDetail.model_validate(response.json())


async def get_discogs_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> DiscogsClient:
    """FastAPI dependency that provides a DiscogsClient instance."""
    return DiscogsClient(settings)
