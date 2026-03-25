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
    """Seed a small set of albums for filter/search testing."""
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
    """Tests for AlbumRepository.get_all() with search and filter options."""

    async def test_returns_all_albums_when_no_filters(
        self, async_session: AsyncSession
    ) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all()

        assert len(result) == 4

    async def test_search_by_artist(self, async_session: AsyncSession) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all(search="clash")

        assert len(result) == 2
        assert all("Clash" in a.artist for a in result)

    async def test_search_by_title(self, async_session: AsyncSession) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all(search="kind of blue")

        assert len(result) == 1
        assert result[0].title == "Kind of Blue"

    async def test_filter_by_genre(self, async_session: AsyncSession) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all(genres=["Jazz"])

        assert len(result) == 1
        assert result[0].artist == "Miles Davis"

    async def test_filter_by_style_tag(self, async_session: AsyncSession) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all(genres=["Punk"])

        assert len(result) == 2

    async def test_filter_by_decade(self, async_session: AsyncSession) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all(decades=[1970])

        assert len(result) == 2
        assert all(1970 <= a.year < 1980 for a in result)

    async def test_combined_search_and_filter(
        self, async_session: AsyncSession
    ) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all(search="clash", decades=[1970])

        assert len(result) == 1
        assert result[0].title == "London Calling"

    async def test_results_ordered_by_artist_then_title(
        self, async_session: AsyncSession
    ) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all()

        artists_titles = [(a.artist, a.title) for a in result]
        assert artists_titles == sorted(artists_titles)

    async def test_no_results_returns_empty_list(
        self, async_session: AsyncSession
    ) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        result = await repo.get_all(search="nonexistent")

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


@pytest.mark.asyncio
class TestAlbumRepositoryGetFilters:
    """Tests for AlbumRepository.get_filters()."""

    async def test_returns_unique_genres_sorted(
        self, async_session: AsyncSession
    ) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        filters = await repo.get_filters()

        assert "Rock" in filters["genres"]
        assert "Jazz" in filters["genres"]
        assert "Punk" in filters["genres"]
        # Verify sorted
        assert filters["genres"] == sorted(filters["genres"])

    async def test_returns_unique_decades_sorted(
        self, async_session: AsyncSession
    ) -> None:
        await _seed_albums(async_session)
        repo = AlbumRepository(async_session)

        filters = await repo.get_filters()

        assert 1950 in filters["decades"]
        assert 1970 in filters["decades"]
        assert 1980 in filters["decades"]
        assert filters["decades"] == sorted(filters["decades"])

    async def test_empty_collection_returns_empty_filters(
        self, async_session: AsyncSession
    ) -> None:
        repo = AlbumRepository(async_session)

        filters = await repo.get_filters()

        assert filters["decades"] == []
        assert filters["genres"] == []
