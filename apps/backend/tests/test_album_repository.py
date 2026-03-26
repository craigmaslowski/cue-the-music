"""Tests for the AlbumRepository — database query layer."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.models.album import Album
from cue_the_music.repositories.album_repository import AlbumRepository


def _make_album(**overrides) -> Album:
    """Helper to create an Album with sensible defaults."""
    defaults = {
        "artist": "Test Artist",
        "cover_art_thumbnail_url": "https://example.com/thumb.jpg",
        "cover_art_url": "https://example.com/cover.jpg",
        "discogs_release_id": "12345",
        "genre_tags": ["Rock"],
        "label": "Test Label",
        "style_tags": ["Punk"],
        "title": "Test Album",
        "year": 1977,
    }
    defaults.update(overrides)
    return Album(**defaults)


async def _seed_albums(session: AsyncSession) -> list[Album]:
    """Seed a small set of albums for testing."""
    albums = [
        _make_album(
            artist="The Clash",
            discogs_release_id="1001",
            genre_tags=["Rock"],
            style_tags=["Punk"],
            title="London Calling",
            year=1979,
        ),
        _make_album(
            artist="Miles Davis",
            discogs_release_id="1002",
            genre_tags=["Jazz"],
            style_tags=["Modal"],
            title="Kind of Blue",
            year=1959,
        ),
        _make_album(
            artist="Kraftwerk",
            discogs_release_id="1003",
            genre_tags=["Electronic"],
            style_tags=["Synth-pop"],
            title="Trans-Europe Express",
            year=1977,
        ),
        _make_album(
            artist="The Clash",
            discogs_release_id="1004",
            genre_tags=["Rock", "Reggae"],
            style_tags=["Punk", "Dub"],
            title="Sandinista!",
            year=1980,
        ),
    ]
    for album in albums:
        session.add(album)
    await session.flush()
    return albums


@pytest.mark.asyncio
class TestAlbumRepositoryGetAll:
    """Tests for AlbumRepository.get_all()."""

    async def test_returns_all_albums(
        self, async_session: AsyncSession
    ) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all()

        assert len(result) == 4

    async def test_results_ordered_by_artist_then_title(
        self, async_session: AsyncSession
    ) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all()

        artists_titles = [(a.artist, a.title) for a in result]
        assert artists_titles == sorted(artists_titles)

    async def test_empty_collection_returns_empty_list(
        self, async_session: AsyncSession
    ) -> None:
        repo = AlbumRepository(async_session)

        result = await repo.get_all()

        assert result == []


@pytest.mark.asyncio
class TestAlbumRepositoryGetById:
    """Tests for AlbumRepository.get_by_id()."""

    async def test_returns_album_when_found(
        self, async_session: AsyncSession
    ) -> None:
        albums = await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_by_id(albums[0].id)

        assert result is not None
        assert result.artist == "The Clash"

    async def test_returns_none_when_not_found(
        self, async_session: AsyncSession
    ) -> None:
        repo = AlbumRepository(async_session)

        result = await repo.get_by_id(9999)

        assert result is None
