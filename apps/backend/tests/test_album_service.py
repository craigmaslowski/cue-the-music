"""Tests for the AlbumService — business logic layer."""

from unittest.mock import AsyncMock

import pytest

from cue_the_music.exceptions.exceptions import AlbumNotFoundError
from cue_the_music.integrations.discogs_client import (
    DiscogsReleaseDetail,
    DiscogsTrack,
)
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
        service = AlbumService(discogs_client=None, repository=mock_repo)

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
        service = AlbumService(discogs_client=None, repository=mock_repo)

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
        service = AlbumService(discogs_client=None, repository=mock_repo)

        result = await service.get_album_detail(42)

        assert result.id == 42
        mock_repo.get_by_id.assert_called_once_with(42)

    async def test_raises_not_found_when_missing(self) -> None:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None
        service = AlbumService(discogs_client=None, repository=mock_repo)

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
        service = AlbumService(discogs_client=None, repository=mock_repo)

        result = await service.get_available_filters()

        assert result == expected
        mock_repo.get_filters.assert_called_once()


@pytest.mark.asyncio
class TestAlbumServiceTracklistCaching:
    """Tests for tracklist lazy-fetch and caching in get_album_detail()."""

    async def test_fetches_tracklist_when_null(self) -> None:
        """When tracklist is null and discogs client is available, fetch it."""
        album = _make_mock_album(album_id=10)
        album.tracklist = None

        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = album
        mock_repo.update_tracklist.return_value = album

        mock_discogs = AsyncMock()
        mock_discogs.get_release_detail.return_value = DiscogsReleaseDetail(
            id=12345,
            tracklist=[
                DiscogsTrack(
                    duration="9:22", position="A1", title="So What", type_="track"
                ),
                DiscogsTrack(
                    duration="9:46",
                    position="A2",
                    title="Freddie Freeloader",
                    type_="track",
                ),
            ],
        )

        service = AlbumService(discogs_client=mock_discogs, repository=mock_repo)
        result = await service.get_album_detail(10)

        # Verify tracklist was fetched and stored
        mock_discogs.get_release_detail.assert_called_once_with(12345)
        mock_repo.update_tracklist.assert_called_once()
        assert result.tracklist is not None
        assert len(result.tracklist) == 2
        assert result.tracklist[0]["title"] == "So What"

    async def test_skips_tracklist_fetch_when_already_cached(self) -> None:
        """When tracklist is already populated, don't call Discogs."""
        album = _make_mock_album(album_id=10)
        album.tracklist = [{"duration": "3:00", "position": "1", "title": "Track 1"}]

        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = album

        mock_discogs = AsyncMock()
        service = AlbumService(discogs_client=mock_discogs, repository=mock_repo)
        result = await service.get_album_detail(10)

        mock_discogs.get_release_detail.assert_not_called()
        assert result.tracklist == [
            {"duration": "3:00", "position": "1", "title": "Track 1"}
        ]

    async def test_skips_tracklist_when_no_discogs_client(self) -> None:
        """When discogs client is None, return album without tracklist."""
        album = _make_mock_album(album_id=10)
        album.tracklist = None

        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = album

        service = AlbumService(discogs_client=None, repository=mock_repo)
        result = await service.get_album_detail(10)

        assert result.tracklist is None

    async def test_tracklist_fetch_failure_does_not_raise(self) -> None:
        """If Discogs API fails during tracklist fetch, return album anyway."""
        album = _make_mock_album(album_id=10)
        album.tracklist = None

        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = album

        mock_discogs = AsyncMock()
        mock_discogs.get_release_detail.side_effect = RuntimeError("API down")

        service = AlbumService(discogs_client=mock_discogs, repository=mock_repo)
        result = await service.get_album_detail(10)

        # Should return album without tracklist, not raise
        assert result.tracklist is None

    async def test_filters_heading_tracks(self) -> None:
        """Section headings (type_ == 'heading') should be excluded."""
        album = _make_mock_album(album_id=10)
        album.tracklist = None

        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = album
        mock_repo.update_tracklist.return_value = album

        mock_discogs = AsyncMock()
        mock_discogs.get_release_detail.return_value = DiscogsReleaseDetail(
            id=12345,
            tracklist=[
                DiscogsTrack(
                    duration="", position="", title="Side A", type_="heading"
                ),
                DiscogsTrack(
                    duration="5:00", position="A1", title="Track One", type_="track"
                ),
            ],
        )

        service = AlbumService(discogs_client=mock_discogs, repository=mock_repo)
        result = await service.get_album_detail(10)

        assert len(result.tracklist) == 1
        assert result.tracklist[0]["title"] == "Track One"
