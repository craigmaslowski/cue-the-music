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

        Uses a dedicated session per page for independent commit boundaries.
        Returns the number of albums processed on this page.
        """
        async with async_session_factory() as session, session.begin():
            for release in releases:
                await self._upsert_album(session, release)
        return len(releases)

    async def _upsert_album(
        self,
        session: AsyncSession,
        release: DiscogsCollectionRelease,
    ) -> None:
        """Insert or update a single album from a Discogs collection release.

        Matches on discogs_release_id. Updates metadata if the album exists,
        inserts a new row if it does not. Tracklist is not touched here --
        it is lazily fetched on detail view.
        """
        info = release.basic_information
        discogs_id = str(info.id)

        # Look up existing album by Discogs release ID
        stmt = select(Album).where(Album.discogs_release_id == discogs_id)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        # Extract artist name (first artist or "Unknown")
        artist_name = info.artists[0].name if info.artists else "Unknown"

        # Extract label name (first label or None)
        label_name = info.labels[0].name if info.labels else None

        if existing:
            # Update existing album metadata (but not tracklist)
            existing.artist = artist_name
            existing.cover_art_thumbnail_url = info.thumb or None
            existing.cover_art_url = info.cover_image or None
            existing.genre_tags = info.genres
            existing.label = label_name
            existing.style_tags = info.styles
            existing.title = info.title
            existing.year = info.year if info.year else None
        else:
            # Insert new album
            album = Album(
                artist=artist_name,
                cover_art_thumbnail_url=info.thumb or None,
                cover_art_url=info.cover_image or None,
                discogs_release_id=discogs_id,
                genre_tags=info.genres,
                label=label_name,
                style_tags=info.styles,
                title=info.title,
                tracklist=None,
                year=info.year if info.year else None,
            )
            session.add(album)


async def get_sync_service(
    discogs_client: Annotated[DiscogsClient, Depends(get_discogs_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SyncService:
    """FastAPI dependency that provides a SyncService instance."""
    return SyncService(discogs_client=discogs_client, settings=settings)
