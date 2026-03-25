"""Tests for the QueueService — business logic layer."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from cue_the_music.exceptions.exceptions import (
    AlbumNotFoundError,
    QueueItemNotFoundError,
    RequestLimitExceededError,
)
from cue_the_music.models.album import Album
from cue_the_music.models.queue_item import QueueItem
from cue_the_music.services.queue_service import GUEST_REQUEST_LIMIT, QueueService


def _make_mock_album(album_id: int = 1) -> Album:
    """Create a mock Album instance."""
    return Album(
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


def _make_service(
    queue_repo=None,
    vote_repo=None,
    now_playing_repo=None,
    album_repo=None,
) -> QueueService:
    """Create a QueueService with optional mock repositories."""
    return QueueService(
        queue_repo=queue_repo or AsyncMock(),
        vote_repo=vote_repo or AsyncMock(),
        now_playing_repo=now_playing_repo or AsyncMock(),
        album_repo=album_repo or AsyncMock(),
    )


@pytest.mark.asyncio
class TestQueueServiceRequestAlbum:
    """Tests for QueueService.request_album()."""

    async def test_adds_album_to_queue(self) -> None:
        album = _make_mock_album(album_id=1)
        album_repo = AsyncMock()
        album_repo.get_by_id.return_value = album

        queue_repo = AsyncMock()
        mock_item = MagicMock(spec=QueueItem)
        mock_item.id = 1
        mock_item.album_id = 1
        mock_item.requested_by_ip = "192.168.1.10"
        mock_item.created_at = "2026-03-25T12:00:00"
        queue_repo.add_to_queue.return_value = mock_item
        queue_repo.count_active_requests.return_value = 0

        service = _make_service(queue_repo=queue_repo, album_repo=album_repo)

        result = await service.request_album(1, "192.168.1.10")

        assert result.id == 1
        queue_repo.add_to_queue.assert_called_once_with(1, "192.168.1.10")

    async def test_raises_not_found_for_missing_album(self) -> None:
        album_repo = AsyncMock()
        album_repo.get_by_id.return_value = None

        service = _make_service(album_repo=album_repo)

        with pytest.raises(AlbumNotFoundError):
            await service.request_album(999, "192.168.1.10")

    async def test_raises_limit_exceeded(self) -> None:
        album = _make_mock_album(album_id=1)
        album_repo = AsyncMock()
        album_repo.get_by_id.return_value = album

        queue_repo = AsyncMock()
        queue_repo.count_active_requests.return_value = GUEST_REQUEST_LIMIT

        service = _make_service(queue_repo=queue_repo, album_repo=album_repo)

        with pytest.raises(RequestLimitExceededError):
            await service.request_album(1, "192.168.1.10")


@pytest.mark.asyncio
class TestQueueServiceCancelRequest:
    """Tests for QueueService.cancel_request()."""

    async def test_cancels_own_request(self) -> None:
        queue_repo = AsyncMock()
        queue_repo.remove_from_queue.return_value = True
        service = _make_service(queue_repo=queue_repo)

        await service.cancel_request(1, "192.168.1.10")

        queue_repo.remove_from_queue.assert_called_once_with(1, ip="192.168.1.10")

    async def test_raises_not_found(self) -> None:
        queue_repo = AsyncMock()
        queue_repo.remove_from_queue.return_value = False
        service = _make_service(queue_repo=queue_repo)

        with pytest.raises(QueueItemNotFoundError):
            await service.cancel_request(999, "192.168.1.10")


@pytest.mark.asyncio
class TestQueueServicePromote:
    """Tests for QueueService.promote_to_now_playing()."""

    async def test_promotes_queue_item(self) -> None:
        mock_item = MagicMock(spec=QueueItem)
        mock_item.id = 1
        mock_item.album_id = 42

        queue_repo = AsyncMock()
        queue_repo.get_queue_item.return_value = mock_item
        queue_repo.remove_from_queue.return_value = True

        now_playing_repo = AsyncMock()

        service = _make_service(
            queue_repo=queue_repo, now_playing_repo=now_playing_repo
        )

        await service.promote_to_now_playing(1)

        queue_repo.remove_from_queue.assert_called_once_with(1)
        now_playing_repo.upsert.assert_called_once_with(42)

    async def test_raises_not_found_for_missing_item(self) -> None:
        queue_repo = AsyncMock()
        queue_repo.get_queue_item.return_value = None

        service = _make_service(queue_repo=queue_repo)

        with pytest.raises(QueueItemNotFoundError):
            await service.promote_to_now_playing(999)


@pytest.mark.asyncio
class TestQueueServiceVoting:
    """Tests for QueueService vote operations."""

    async def test_cast_vote_validates_queue_item(self) -> None:
        queue_repo = AsyncMock()
        queue_repo.get_queue_item.return_value = None
        service = _make_service(queue_repo=queue_repo)

        with pytest.raises(QueueItemNotFoundError):
            await service.cast_vote(999, "192.168.1.10", 1)

    async def test_cast_vote_delegates_to_repo(self) -> None:
        mock_item = MagicMock(spec=QueueItem)
        queue_repo = AsyncMock()
        queue_repo.get_queue_item.return_value = mock_item

        vote_repo = AsyncMock()
        service = _make_service(queue_repo=queue_repo, vote_repo=vote_repo)

        await service.cast_vote(1, "192.168.1.10", 1)

        vote_repo.upsert_vote.assert_called_once_with(1, "192.168.1.10", 1)

    async def test_remove_vote_not_found(self) -> None:
        vote_repo = AsyncMock()
        vote_repo.remove_vote.return_value = False
        service = _make_service(vote_repo=vote_repo)

        with pytest.raises(QueueItemNotFoundError):
            await service.remove_vote(999, "192.168.1.10")


@pytest.mark.asyncio
class TestQueueServiceGetQueueState:
    """Tests for QueueService.get_queue_state()."""

    async def test_returns_empty_state(self) -> None:
        queue_repo = AsyncMock()
        queue_repo.get_queue_items.return_value = []
        queue_repo.get_vote_aggregates.return_value = {}

        now_playing_repo = AsyncMock()
        now_playing_repo.get_current.return_value = None

        service = _make_service(
            queue_repo=queue_repo, now_playing_repo=now_playing_repo
        )

        result = await service.get_queue_state("192.168.1.10")

        assert result.now_playing is None
        assert result.queue == []
        assert result.count == 0
