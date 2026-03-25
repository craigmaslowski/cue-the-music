"""Tests for SyncService — collection sync business logic."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cue_the_music.config import Settings
from cue_the_music.exceptions.exceptions import DiscogsSyncError
from cue_the_music.integrations.discogs_client import (
    DiscogsArtist,
    DiscogsBasicInformation,
    DiscogsCollectionRelease,
    DiscogsCollectionResponse,
    DiscogsLabel,
    DiscogsPagination,
)
from cue_the_music.models.album import Album
from cue_the_music.services.sync_service import SyncService


def _make_settings() -> Settings:
    """Create test settings."""
    return Settings(
        DISCOGS_TOKEN="test-token",
        DISCOGS_USERNAME="testuser",
        HOST_PIN="1234",
    )


def _make_collection_response(
    releases: list[DiscogsCollectionRelease],
    page: int = 1,
    pages: int = 1,
) -> DiscogsCollectionResponse:
    """Build a DiscogsCollectionResponse with given releases."""
    return DiscogsCollectionResponse(
        pagination=DiscogsPagination(page=page, pages=pages, per_page=100),
        releases=releases,
    )


def _make_release(
    release_id: int = 12345,
    artist: str = "Miles Davis",
    title: str = "Kind of Blue",
    year: int = 1959,
) -> DiscogsCollectionRelease:
    """Build a single DiscogsCollectionRelease."""
    return DiscogsCollectionRelease(
        basic_information=DiscogsBasicInformation(
            artists=[DiscogsArtist(name=artist)],
            cover_image=f"https://img.discogs.com/{release_id}_full.jpg",
            genres=["Jazz"],
            id=release_id,
            labels=[DiscogsLabel(name="Columbia")],
            styles=["Modal"],
            thumb=f"https://img.discogs.com/{release_id}_thumb.jpg",
            title=title,
            year=year,
        )
    )


@pytest.mark.asyncio
class TestSyncServiceSyncCollection:
    """Tests for SyncService.sync_collection()."""

    async def test_single_page_sync_inserts_albums(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """Syncing a single-page collection creates album rows."""
        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[
                _make_release(12345, "Miles Davis", "Kind of Blue", 1959),
                _make_release(67890, "The Clash", "London Calling", 1979),
            ],
            page=1,
            pages=1,
        )

        # Patch the session factory to use our test engine
        test_session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )
        with patch(
            "cue_the_music.services.sync_service.async_session_factory",
            test_session_factory,
        ):
            service = SyncService(
                discogs_client=mock_client, settings=_make_settings()
            )
            result = await service.sync_collection()

        assert result.albums_synced == 2
        assert result.total_pages == 1

        # Verify albums in DB
        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 2
            artists = sorted(a.artist for a in albums)
            assert artists == ["Miles Davis", "The Clash"]

    async def test_multi_page_sync(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """Syncing a multi-page collection fetches all pages."""
        page1 = _make_collection_response(
            releases=[_make_release(111, "Artist A", "Album A")],
            page=1,
            pages=2,
        )
        page2 = _make_collection_response(
            releases=[_make_release(222, "Artist B", "Album B")],
            page=2,
            pages=2,
        )
        mock_client = AsyncMock()
        mock_client.get_collection_page.side_effect = [page1, page2]

        test_session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )
        with patch(
            "cue_the_music.services.sync_service.async_session_factory",
            test_session_factory,
        ):
            service = SyncService(
                discogs_client=mock_client, settings=_make_settings()
            )
            result = await service.sync_collection()

        assert result.albums_synced == 2
        assert result.total_pages == 2
        assert mock_client.get_collection_page.call_count == 2

    async def test_upsert_updates_existing_album(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """Re-syncing updates metadata on existing albums instead of duplicating."""
        # Seed an existing album
        test_session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )
        async with test_session_factory() as session, session.begin():
            session.add(
                Album(
                    artist="Old Artist Name",
                    cover_art_url="https://old.jpg",
                    discogs_release_id="12345",
                    genre_tags=["Rock"],
                    title="Old Title",
                    year=1970,
                )
            )

        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[_make_release(12345, "Miles Davis", "Kind of Blue", 1959)],
        )

        with patch(
            "cue_the_music.services.sync_service.async_session_factory",
            test_session_factory,
        ):
            service = SyncService(
                discogs_client=mock_client, settings=_make_settings()
            )
            result = await service.sync_collection()

        assert result.albums_synced == 1

        # Verify the album was updated, not duplicated
        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 1
            assert albums[0].artist == "Miles Davis"
            assert albums[0].title == "Kind of Blue"
            assert albums[0].year == 1959

    async def test_additive_only_does_not_delete(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """Albums not in the Discogs response are left untouched (additive sync)."""
        test_session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )
        async with test_session_factory() as session, session.begin():
            session.add(
                Album(
                    artist="Existing Artist",
                    discogs_release_id="99999",
                    genre_tags=["Electronic"],
                    title="Existing Album",
                    year=2000,
                )
            )

        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[_make_release(12345, "Miles Davis", "Kind of Blue", 1959)],
        )

        with patch(
            "cue_the_music.services.sync_service.async_session_factory",
            test_session_factory,
        ):
            service = SyncService(
                discogs_client=mock_client, settings=_make_settings()
            )
            await service.sync_collection()

        # Both albums should exist
        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 2

    async def test_api_failure_raises_sync_error(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """A Discogs API failure is wrapped in DiscogsSyncError."""
        mock_client = AsyncMock()
        mock_client.get_collection_page.side_effect = RuntimeError("Network error")

        test_session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )
        with patch(
            "cue_the_music.services.sync_service.async_session_factory",
            test_session_factory,
        ):
            service = SyncService(
                discogs_client=mock_client, settings=_make_settings()
            )
            with pytest.raises(DiscogsSyncError):
                await service.sync_collection()
