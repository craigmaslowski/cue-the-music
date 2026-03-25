"""Tests for the NowPlayingRepository — database query layer."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.models.album import Album
from cue_the_music.repositories.now_playing_repository import NowPlayingRepository


async def _seed_album(session: AsyncSession, release_id: str = "np001") -> Album:
    """Seed a single album and return it."""
    album = Album(
        artist="Test Artist",
        cover_art_thumbnail_url="https://example.com/thumb.jpg",
        cover_art_url="https://example.com/cover.jpg",
        discogs_release_id=release_id,
        genre_tags=["Rock"],
        label="Test Label",
        style_tags=["Punk"],
        title="Test Album",
        year=1977,
    )
    session.add(album)
    await session.flush()
    return album


@pytest.mark.asyncio
class TestNowPlayingRepositoryUpsert:
    """Tests for NowPlayingRepository.upsert()."""

    async def test_inserts_now_playing(self, async_session: AsyncSession) -> None:
        album = await _seed_album(async_session, "np001")
        repo = NowPlayingRepository(async_session)

        await repo.upsert(album.id)
        await async_session.flush()

        current = await repo.get_current()
        assert current is not None
        assert current.album_id == album.id

    async def test_upsert_replaces_existing(
        self, async_session: AsyncSession
    ) -> None:
        album1 = await _seed_album(async_session, "np002")
        album2 = await _seed_album(async_session, "np003")
        repo = NowPlayingRepository(async_session)

        await repo.upsert(album1.id)
        await async_session.flush()
        await repo.upsert(album2.id)
        await async_session.flush()

        current = await repo.get_current()
        assert current is not None
        assert current.album_id == album2.id


@pytest.mark.asyncio
class TestNowPlayingRepositoryGetCurrent:
    """Tests for NowPlayingRepository.get_current()."""

    async def test_returns_none_when_empty(
        self, async_session: AsyncSession
    ) -> None:
        repo = NowPlayingRepository(async_session)

        current = await repo.get_current()

        assert current is None


@pytest.mark.asyncio
class TestNowPlayingRepositoryClear:
    """Tests for NowPlayingRepository.clear()."""

    async def test_clears_now_playing(self, async_session: AsyncSession) -> None:
        album = await _seed_album(async_session, "np004")
        repo = NowPlayingRepository(async_session)
        await repo.upsert(album.id)
        await async_session.flush()

        result = await repo.clear()

        assert result is True
        current = await repo.get_current()
        assert current is None

    async def test_clear_when_empty(self, async_session: AsyncSession) -> None:
        repo = NowPlayingRepository(async_session)

        result = await repo.clear()

        assert result is False
