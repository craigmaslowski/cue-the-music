"""Tests for the AlbumService — business logic layer."""

from unittest.mock import AsyncMock

import pytest

from cue_the_music.exceptions.exceptions import AlbumNotFoundError
from cue_the_music.models.album import Album
from cue_the_music.services.album_service import AlbumService


def _make_mock_album(album_id: int = 1) -> Album:
    """Create a mock Album instance."""
    album = Album(
        artist="Test Artist",
        cover_art_thumbnail_url="https://example.com/thumb.jpg",
        cover_art_url="https://example.com/cover.jpg",
        discogs_release_id="12345",
        genre_tags=["Rock"],
        id=album_id,
        label="Test Label",
        style_tags=["Punk"],
        title="Test Album",
        year=1977,
    )
    return album


@pytest.mark.asyncio
class TestAlbumServiceGetAlbums:
    """Tests for AlbumService.get_albums()."""

    async def test_delegates_to_repository(self) -> None:
        mock_repo = AsyncMock()
        mock_repo.get_all.return_value = [_make_mock_album()]
        service = AlbumService(mock_repo)

        result = await service.get_albums(search="test", genres=["Rock"])

        mock_repo.get_all.assert_called_once_with(
            decades=None,
            genres=["Rock"],
            search="test",
        )
        assert len(result) == 1

    async def test_passes_all_filters(self) -> None:
        mock_repo = AsyncMock()
        mock_repo.get_all.return_value = []
        service = AlbumService(mock_repo)

        await service.get_albums(
            decades=[1970],
            genres=["Jazz"],
            search="miles",
        )

        mock_repo.get_all.assert_called_once_with(
            decades=[1970],
            genres=["Jazz"],
            search="miles",
        )


@pytest.mark.asyncio
class TestAlbumServiceGetAlbumDetail:
    """Tests for AlbumService.get_album_detail()."""

    async def test_returns_album_when_found(self) -> None:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = _make_mock_album(album_id=42)
        service = AlbumService(mock_repo)

        result = await service.get_album_detail(42)

        assert result.id == 42
        mock_repo.get_by_id.assert_called_once_with(42)

    async def test_raises_not_found_when_missing(self) -> None:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None
        service = AlbumService(mock_repo)

        with pytest.raises(AlbumNotFoundError) as exc_info:
            await service.get_album_detail(999)

        assert exc_info.value.album_id == 999


@pytest.mark.asyncio
class TestAlbumServiceGetAvailableFilters:
    """Tests for AlbumService.get_available_filters()."""

    async def test_delegates_to_repository(self) -> None:
        mock_repo = AsyncMock()
        expected = {"decades": [1970, 1980], "genres": ["Jazz", "Rock"]}
        mock_repo.get_filters.return_value = expected
        service = AlbumService(mock_repo)

        result = await service.get_available_filters()

        assert result == expected
        mock_repo.get_filters.assert_called_once()
