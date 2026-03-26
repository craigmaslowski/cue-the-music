"""Tests for album API endpoints using httpx AsyncClient."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from cue_the_music.models.album import Album


async def _seed_via_session(async_engine, albums_data: list[dict]) -> None:
    """Insert albums directly via a session for endpoint testing."""
    session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
    async with session_factory() as session, session.begin():
        for data in albums_data:
            session.add(Album(**data))


SAMPLE_ALBUMS = [
    {
        "artist": "Miles Davis",
        "cover_art_thumbnail_url": "https://example.com/miles_thumb.jpg",
        "cover_art_url": "https://example.com/miles.jpg",
        "discogs_release_id": "2001",
        "genre_tags": ["Jazz"],
        "label": "Columbia",
        "style_tags": ["Modal"],
        "title": "Kind of Blue",
        "year": 1959,
    },
    {
        "artist": "The Clash",
        "cover_art_thumbnail_url": "https://example.com/clash_thumb.jpg",
        "cover_art_url": "https://example.com/clash.jpg",
        "discogs_release_id": "2002",
        "genre_tags": ["Rock"],
        "label": "CBS",
        "style_tags": ["Punk"],
        "title": "London Calling",
        "year": 1979,
    },
]


@pytest.mark.asyncio
class TestListAlbumsEndpoint:
    """Tests for GET /api/albums."""

    async def test_returns_all_albums(
        self, client: AsyncClient, async_engine
    ) -> None:
        await _seed_via_session(async_engine, SAMPLE_ALBUMS)

        response = await client.get("/api/albums")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["albums"]) == 2

    async def test_empty_collection(self, client: AsyncClient) -> None:
        response = await client.get("/api/albums")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["albums"] == []


@pytest.mark.asyncio
class TestGetAlbumEndpoint:
    """Tests for GET /api/albums/{album_id}."""

    async def test_returns_album_by_id(
        self, client: AsyncClient, async_engine
    ) -> None:
        await _seed_via_session(async_engine, SAMPLE_ALBUMS[:1])

        response = await client.get("/api/albums/1")

        assert response.status_code == 200
        data = response.json()
        assert data["artist"] == "Miles Davis"
        assert data["title"] == "Kind of Blue"

    async def test_returns_404_for_missing_album(
        self, client: AsyncClient
    ) -> None:
        response = await client.get("/api/albums/9999")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Album not found."
