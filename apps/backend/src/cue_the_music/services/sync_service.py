"""Service for syncing the host's Discogs collection into the local database.

Handles full collection pagination, upsert logic, and per-page commits.
Additive only -- albums removed from Discogs are not deleted locally.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.config import Settings, get_settings
from cue_the_music.dependencies.database import async_session_factory
from cue_the_music.exceptions.exceptions import DiscogsSyncError
from cue_the_music.integrations.discogs_client import (
    DiscogsClient,
    DiscogsCollectionRelease,
    get_discogs_client,
)
from cue_the_music.models.album import Album

logger = logging.getLogger(__name__)


@dataclass
class ResolvedMasterData:
    """Year and tracklist resolved from a Discogs master release."""

    tracklist: list[dict[str, str]] | None
    year: int | None


@dataclass
class SyncResult:
    """Summary of a completed sync operation."""

    albums_synced: int
    total_pages: int


class SyncService:
    """Orchestrates syncing the host's Discogs collection to the local DB.

    Fetches all pages of the collection, upserts albums by discogs_release_id,
    and commits per page for bounded memory and transaction scope.
    """

    def __init__(self, discogs_client: DiscogsClient, settings: Settings) -> None:
        self._discogs_client = discogs_client
        self._settings = settings

    async def sync_collection(self) -> SyncResult:
        """Sync the full Discogs collection into the albums table.

        Pages through the collection endpoint, upserting each album by
        discogs_release_id. Commits after each page for bounded transactions.
        Uses asyncio.sleep(0) between pages for event loop responsiveness.

        Returns:
            SyncResult with count of albums processed and total pages.
        """
        username = self._settings.DISCOGS_USERNAME
        albums_synced = 0
        current_page = 1
        total_pages = 1

        try:
            # Fetch the first page to learn total page count
            first_response = await self._discogs_client.get_collection_page(
                username, page=1
            )
            total_pages = first_response.pagination.pages

            # Process the first page
            albums_synced += await self._upsert_page(first_response.releases)

            # Process remaining pages
            for page_num in range(2, total_pages + 1):
                current_page = page_num
                await asyncio.sleep(0)  # yield to event loop between pages

                page_response = await self._discogs_client.get_collection_page(
                    username, page=page_num
                )
                albums_synced += await self._upsert_page(page_response.releases)

        except Exception as exc:
            logger.exception(
                "Discogs sync failed on page %d of %d", current_page, total_pages
            )
            raise DiscogsSyncError(
                detail=f"Sync failed on page {current_page} of {total_pages}"
            ) from exc

        logger.info(
            "Discogs sync complete: %d albums across %d pages",
            albums_synced,
            total_pages,
        )
        return SyncResult(albums_synced=albums_synced, total_pages=total_pages)

    async def _upsert_page(
        self, releases: list[DiscogsCollectionRelease]
    ) -> int:
        """Upsert a page of releases into the albums table.

        Resolves master release years and tracklists outside the DB transaction
        to avoid holding the write lock during rate-limited API calls. Then
        upserts all albums in a single per-page transaction.
        """
        # Phase 1: resolve master data (HTTP calls, no DB lock)
        resolved_data = await self._resolve_master_data_for_page(releases)

        # Phase 2: upsert albums (DB writes, no HTTP calls)
        async with async_session_factory() as session, session.begin():
            for release in releases:
                discogs_id = str(release.basic_information.id)
                await self._upsert_album(
                    session, release, resolved_data.get(discogs_id)
                )
        return len(releases)

    async def _resolve_master_data_for_page(
        self,
        releases: list[DiscogsCollectionRelease],
    ) -> dict[str, ResolvedMasterData]:
        """Resolve original release years and tracklists for a page of releases.

        Checks the DB for already-resolved data to skip redundant API calls.
        Returns a mapping of discogs_release_id -> ResolvedMasterData.
        """
        resolved: dict[str, ResolvedMasterData] = {}

        # Check which albums already have resolved master data in the DB
        already_resolved: dict[str, tuple[int | None, int | None, bool]] = {}
        async with async_session_factory() as session:
            for release in releases:
                discogs_id = str(release.basic_information.id)
                stmt = select(Album).where(Album.discogs_release_id == discogs_id)
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    already_resolved[discogs_id] = (
                        existing.discogs_master_id,
                        existing.year,
                        existing.tracklist is not None,
                    )

        for release in releases:
            info = release.basic_information
            discogs_id = str(info.id)
            master_id = info.master_id

            # Skip master fetch if year and tracklist already resolved from this master
            cached = already_resolved.get(discogs_id)
            if cached and cached[0] == master_id and cached[1] and cached[2]:
                resolved[discogs_id] = ResolvedMasterData(
                    tracklist=None,  # None signals "keep existing"
                    year=cached[1],
                )
            else:
                resolved[discogs_id] = await self._resolve_master(
                    master_id, info.year
                )

        return resolved

    async def _resolve_master(
        self,
        master_id: int,
        release_year: int,
    ) -> ResolvedMasterData:
        """Resolve year and tracklist from master release.

        If master_id is valid (> 0), fetches the master release and extracts
        both year and tracklist. Falls back to release_year on failure or when
        no master exists. Returns None tracklist when no master is available.
        """
        if master_id > 0:
            try:
                master = await self._discogs_client.get_master_release(master_id)
                year = master.year if master.year > 0 else (
                    release_year if release_year > 0 else None
                )
                # Extract tracklist, filtering section headings
                tracklist = [
                    {
                        "duration": track.duration,
                        "position": track.position,
                        "title": track.title,
                    }
                    for track in master.tracklist
                    if track.type_ != "heading"
                ] or None
                return ResolvedMasterData(tracklist=tracklist, year=year)
            except Exception:
                logger.warning(
                    "Failed to fetch master %d, using release year",
                    master_id,
                    exc_info=True,
                )
        year = release_year if release_year > 0 else None
        return ResolvedMasterData(tracklist=None, year=year)

    async def _upsert_album(
        self,
        session: AsyncSession,
        release: DiscogsCollectionRelease,
        master_data: ResolvedMasterData | None,
    ) -> None:
        """Insert or update a single album from a Discogs collection release.

        Matches on discogs_release_id. Updates metadata if the album exists,
        inserts a new row if it does not.
        """
        info = release.basic_information
        discogs_id = str(info.id)
        master_id = info.master_id

        resolved_year = master_data.year if master_data else (
            info.year if info.year > 0 else None
        )
        resolved_tracklist = master_data.tracklist if master_data else None

        # Look up existing album by Discogs release ID
        stmt = select(Album).where(Album.discogs_release_id == discogs_id)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        # Extract artist name (first artist or "Unknown")
        artist_name = info.artists[0].name if info.artists else "Unknown"

        # Extract label name (first label or None)
        label_name = info.labels[0].name if info.labels else None

        if existing:
            # Update existing album metadata
            existing.artist = artist_name
            existing.cover_art_thumbnail_url = info.thumb or None
            existing.cover_art_url = info.cover_image or None
            existing.discogs_master_id = master_id if master_id > 0 else None
            existing.genre_tags = info.genres
            existing.label = label_name
            existing.style_tags = info.styles
            existing.title = info.title
            existing.year = resolved_year
            # Only set tracklist if currently NULL and we have new data
            if existing.tracklist is None and resolved_tracklist is not None:
                existing.tracklist = resolved_tracklist
        else:
            # Insert new album
            album = Album(
                artist=artist_name,
                cover_art_thumbnail_url=info.thumb or None,
                cover_art_url=info.cover_image or None,
                discogs_master_id=master_id if master_id > 0 else None,
                discogs_release_id=discogs_id,
                genre_tags=info.genres,
                label=label_name,
                style_tags=info.styles,
                title=info.title,
                tracklist=resolved_tracklist,
                year=resolved_year,
            )
            session.add(album)


async def get_sync_service(
    discogs_client: Annotated[DiscogsClient, Depends(get_discogs_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SyncService:
    """FastAPI dependency that provides a SyncService instance."""
    return SyncService(discogs_client=discogs_client, settings=settings)
