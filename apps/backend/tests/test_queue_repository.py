"""Tests for the QueueRepository — database query layer."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.exceptions.exceptions import AlbumAlreadyQueuedError
from cue_the_music.models.album import Album
from cue_the_music.repositories.queue_repository import QueueRepository


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


async def _seed_album(session: AsyncSession, **overrides) -> Album:
    """Seed a single album and return it."""
    album = _make_album(**overrides)
    session.add(album)
    await session.flush()
    return album


@pytest.mark.asyncio
class TestQueueRepositoryAddToQueue:
    """Tests for QueueRepository.add_to_queue()."""

    async def test_adds_item_to_queue(self, async_session: AsyncSession) -> None:
        album = await _seed_album(async_session, discogs_release_id="1001")
        repo = QueueRepository(async_session)

        item = await repo.add_to_queue(album.id, "192.168.1.10")

        assert item.album_id == album.id
        assert item.requested_by_ip == "192.168.1.10"
        assert item.id is not None

    async def test_duplicate_album_raises_already_queued(
        self, async_session: AsyncSession
    ) -> None:
        album = await _seed_album(async_session, discogs_release_id="1002")
        repo = QueueRepository(async_session)

        await repo.add_to_queue(album.id, "192.168.1.10")

        with pytest.raises(AlbumAlreadyQueuedError):
            await repo.add_to_queue(album.id, "192.168.1.11")

    async def test_different_albums_allowed(
        self, async_session: AsyncSession
    ) -> None:
        album1 = await _seed_album(async_session, discogs_release_id="1003")
        album2 = await _seed_album(async_session, discogs_release_id="1004")
        repo = QueueRepository(async_session)

        item1 = await repo.add_to_queue(album1.id, "192.168.1.10")
        item2 = await repo.add_to_queue(album2.id, "192.168.1.10")

        assert item1.id != item2.id


@pytest.mark.asyncio
class TestQueueRepositoryRemoveFromQueue:
    """Tests for QueueRepository.remove_from_queue()."""

    async def test_removes_item(self, async_session: AsyncSession) -> None:
        album = await _seed_album(async_session, discogs_release_id="2001")
        repo = QueueRepository(async_session)
        item = await repo.add_to_queue(album.id, "192.168.1.10")

        result = await repo.remove_from_queue(item.id)

        assert result is True

    async def test_returns_false_for_nonexistent(
        self, async_session: AsyncSession
    ) -> None:
        repo = QueueRepository(async_session)

        result = await repo.remove_from_queue(9999)

        assert result is False

    async def test_ip_ownership_check(self, async_session: AsyncSession) -> None:
        album = await _seed_album(async_session, discogs_release_id="2002")
        repo = QueueRepository(async_session)
        item = await repo.add_to_queue(album.id, "192.168.1.10")

        # Wrong IP should not remove
        result = await repo.remove_from_queue(item.id, ip="192.168.1.99")
        assert result is False

        # Correct IP should remove
        result = await repo.remove_from_queue(item.id, ip="192.168.1.10")
        assert result is True


@pytest.mark.asyncio
class TestQueueRepositoryGetQueueItems:
    """Tests for QueueRepository.get_queue_items()."""

    async def test_returns_items_ordered_by_id(
        self, async_session: AsyncSession
    ) -> None:
        album1 = await _seed_album(async_session, discogs_release_id="3001")
        album2 = await _seed_album(async_session, discogs_release_id="3002")
        album3 = await _seed_album(async_session, discogs_release_id="3003")
        repo = QueueRepository(async_session)

        await repo.add_to_queue(album1.id, "192.168.1.10")
        await repo.add_to_queue(album2.id, "192.168.1.11")
        await repo.add_to_queue(album3.id, "192.168.1.12")

        items = await repo.get_queue_items()

        assert len(items) == 3
        assert items[0].album_id == album1.id
        assert items[1].album_id == album2.id
        assert items[2].album_id == album3.id

    async def test_empty_queue(self, async_session: AsyncSession) -> None:
        repo = QueueRepository(async_session)

        items = await repo.get_queue_items()

        assert items == []


@pytest.mark.asyncio
class TestQueueRepositoryCountActiveRequests:
    """Tests for QueueRepository.count_active_requests()."""

    async def test_counts_by_ip(self, async_session: AsyncSession) -> None:
        album1 = await _seed_album(async_session, discogs_release_id="4001")
        album2 = await _seed_album(async_session, discogs_release_id="4002")
        repo = QueueRepository(async_session)

        await repo.add_to_queue(album1.id, "192.168.1.10")
        await repo.add_to_queue(album2.id, "192.168.1.10")

        count = await repo.count_active_requests("192.168.1.10")
        assert count == 2

        count_other = await repo.count_active_requests("192.168.1.99")
        assert count_other == 0


@pytest.mark.asyncio
class TestQueueRepositoryGetQueueItem:
    """Tests for QueueRepository.get_queue_item()."""

    async def test_returns_item(self, async_session: AsyncSession) -> None:
        album = await _seed_album(async_session, discogs_release_id="5001")
        repo = QueueRepository(async_session)
        item = await repo.add_to_queue(album.id, "192.168.1.10")

        result = await repo.get_queue_item(item.id)

        assert result is not None
        assert result.id == item.id

    async def test_returns_none_for_missing(
        self, async_session: AsyncSession
    ) -> None:
        repo = QueueRepository(async_session)

        result = await repo.get_queue_item(9999)

        assert result is None
