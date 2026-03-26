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
    DiscogsMasterRelease,
    DiscogsPagination,
    DiscogsTrack,
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
    master_id: int = 0,
) -> DiscogsCollectionRelease:
    """Build a single DiscogsCollectionRelease."""
    return DiscogsCollectionRelease(
        basic_information=DiscogsBasicInformation(
            artists=[DiscogsArtist(name=artist)],
            cover_image=f"https://img.discogs.com/{release_id}_full.jpg",
            genres=["Jazz"],
            id=release_id,
            labels=[DiscogsLabel(name="Columbia")],
            master_id=master_id,
            styles=["Modal"],
            thumb=f"https://img.discogs.com/{release_id}_thumb.jpg",
            title=title,
            year=year,
        ),
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


@pytest.mark.asyncio
class TestMasterReleaseYearResolution:
    """Tests for original release year resolution via master release."""

    async def test_uses_master_year_over_release_year(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """When master_id is set, the master's year is used instead of the pressing year."""
        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[
                _make_release(
                    12345, "The Beatles", "Abbey Road", year=2020, master_id=5678
                ),
            ],
        )
        mock_client.get_master_release.return_value = DiscogsMasterRelease(
            id=5678,
            tracklist=[
                DiscogsTrack(
                    duration="7:47", position="A1", title="Come Together", type_="track"
                ),
                DiscogsTrack(
                    duration="3:26", position="A2", title="Something", type_="track"
                ),
            ],
            year=1969,
        )

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
            await service.sync_collection()

        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 1
            assert albums[0].year == 1969
            assert albums[0].discogs_master_id == 5678

    async def test_persists_tracklist_from_master(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """Tracklist from master release is persisted during sync."""
        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[
                _make_release(12345, "Artist", "Album", year=2020, master_id=5678),
            ],
        )
        mock_client.get_master_release.return_value = DiscogsMasterRelease(
            id=5678,
            tracklist=[
                DiscogsTrack(
                    duration="5:00", position="A1", title="Track One", type_="track"
                ),
                DiscogsTrack(
                    duration="", position="", title="Side B", type_="heading"
                ),
                DiscogsTrack(
                    duration="3:30", position="B1", title="Track Two", type_="track"
                ),
            ],
            year=1969,
        )

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
            await service.sync_collection()

        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 1
            tracklist = albums[0].tracklist
            assert tracklist is not None
            # Heading tracks should be filtered out
            assert len(tracklist) == 2
            assert tracklist[0]["title"] == "Track One"
            assert tracklist[1]["title"] == "Track Two"

    async def test_tracklist_null_without_master(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """Albums without a master_id have tracklist=NULL (lazy-fetch fallback)."""
        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[
                _make_release(12345, "Artist", "Album", year=1985, master_id=0),
            ],
        )

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
            await service.sync_collection()

        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 1
            assert albums[0].tracklist is None

    async def test_resync_does_not_overwrite_existing_tracklist(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """Re-sync preserves an existing tracklist (may have been lazy-fetched)."""
        test_session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )
        # Seed album with a lazy-fetched tracklist
        async with test_session_factory() as session, session.begin():
            session.add(
                Album(
                    artist="Artist",
                    discogs_master_id=5678,
                    discogs_release_id="12345",
                    genre_tags=["Rock"],
                    title="Album",
                    tracklist=[{"duration": "4:00", "position": "1", "title": "Original"}],
                    year=1969,
                )
            )

        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[
                _make_release(12345, "Artist", "Album", year=2020, master_id=5678),
            ],
        )

        with patch(
            "cue_the_music.services.sync_service.async_session_factory",
            test_session_factory,
        ):
            service = SyncService(
                discogs_client=mock_client, settings=_make_settings()
            )
            await service.sync_collection()

        # Master fetch should be skipped (year + tracklist already cached)
        mock_client.get_master_release.assert_not_called()

        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 1
            # Original tracklist preserved
            assert albums[0].tracklist[0]["title"] == "Original"

    async def test_falls_back_to_release_year_without_master(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """When master_id is 0, the release's own year is used."""
        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[
                _make_release(12345, "Artist", "Album", year=1985, master_id=0),
            ],
        )

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
            await service.sync_collection()

        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 1
            assert albums[0].year == 1985
            assert albums[0].discogs_master_id is None
        mock_client.get_master_release.assert_not_called()

    async def test_falls_back_on_master_fetch_failure(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """When master fetch fails, falls back to release year without aborting sync."""
        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[
                _make_release(
                    12345, "Artist", "Album", year=2020, master_id=9999
                ),
            ],
        )
        mock_client.get_master_release.side_effect = RuntimeError("404 Not Found")

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

        assert result.albums_synced == 1
        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 1
            assert albums[0].year == 2020  # falls back to release year

    async def test_skips_master_fetch_when_already_resolved(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """Re-sync skips master fetch when master_id matches, year is set, and tracklist exists."""
        test_session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )
        # Seed album with resolved master year and tracklist
        async with test_session_factory() as session, session.begin():
            session.add(
                Album(
                    artist="The Beatles",
                    discogs_master_id=5678,
                    discogs_release_id="12345",
                    genre_tags=["Rock"],
                    title="Abbey Road",
                    tracklist=[{"duration": "7:47", "position": "A1", "title": "Come Together"}],
                    year=1969,
                )
            )

        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[
                _make_release(
                    12345, "The Beatles", "Abbey Road", year=2020, master_id=5678
                ),
            ],
        )

        with patch(
            "cue_the_music.services.sync_service.async_session_factory",
            test_session_factory,
        ):
            service = SyncService(
                discogs_client=mock_client, settings=_make_settings()
            )
            await service.sync_collection()

        # Master fetch should NOT have been called — year already resolved
        mock_client.get_master_release.assert_not_called()

        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 1
            assert albums[0].year == 1969  # preserved, not overwritten with 2020

    async def test_year_none_when_both_sources_zero(
        self, async_engine, async_session: AsyncSession
    ) -> None:
        """When both master year and release year are 0, year is None."""
        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = _make_collection_response(
            releases=[
                _make_release(12345, "Unknown", "Unknown Album", year=0, master_id=999),
            ],
        )
        mock_client.get_master_release.return_value = DiscogsMasterRelease(
            id=999, year=0
        )

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
            await service.sync_collection()

        async with test_session_factory() as session:
            albums = (await session.execute(select(Album))).scalars().all()
            assert len(albums) == 1
            assert albums[0].year is None
