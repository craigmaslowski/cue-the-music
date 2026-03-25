"""Service layer for album business logic.

Services orchestrate calls to repositories and contain business rules.
They never access the database session directly.
"""

import logging
from typing import Annotated

from fastapi import Depends

from cue_the_music.exceptions.exceptions import AlbumNotFoundError
from cue_the_music.integrations.discogs_client import DiscogsClient
from cue_the_music.models.album import Album
from cue_the_music.repositories.album_repository import (
    AlbumRepository,
    get_album_repository,
)

logger = logging.getLogger(__name__)


class AlbumService:
    """Business logic for album operations."""

    def __init__(
        self,
        discogs_client: DiscogsClient | None,
        repository: AlbumRepository,
    ) -> None:
        self._discogs_client = discogs_client
        self._repository = repository

    async def get_album_detail(self, album_id: int) -> Album:
        """Retrieve a single album by ID, raising if not found.

        If the album's tracklist is null and a DiscogsClient is available,
        fetches the tracklist from Discogs and caches it on the album.
        """
        album = await self._repository.get_by_id(album_id)
        if album is None:
            raise AlbumNotFoundError(album_id)

        # Lazy-fetch and cache tracklist from Discogs if missing
        if album.tracklist is None and self._discogs_client is not None:
            await self._fetch_and_cache_tracklist(album)

        return album

    async def _fetch_and_cache_tracklist(self, album: Album) -> None:
        """Fetch tracklist from Discogs API and store it on the album.

        Fails silently -- a missing tracklist is not a fatal error.
        The next detail request will retry.
        """
        try:
            release_id = int(album.discogs_release_id)
            detail = await self._discogs_client.get_release_detail(release_id)  # type: ignore[union-attr]
            tracklist = [
                {
                    "duration": track.duration,
                    "position": track.position,
                    "title": track.title,
                }
                for track in detail.tracklist
                if track.type_ != "heading"  # skip section headings
            ]
            await self._repository.update_tracklist(album.id, tracklist)
            album.tracklist = tracklist
        except Exception:
            logger.warning(
                "Failed to fetch tracklist for album %d (discogs_release_id=%s)",
                album.id,
                album.discogs_release_id,
                exc_info=True,
            )

    async def get_albums(
        self,
        decades: list[int] | None = None,
        genres: list[str] | None = None,
        search: str | None = None,
    ) -> list[Album]:
        """Retrieve albums with optional search and filter criteria."""
        return await self._repository.get_all(
            decades=decades,
            genres=genres,
            search=search,
        )

    async def get_available_filters(self) -> dict[str, list]:
        """Return available genre and decade filter values from the collection."""
        return await self._repository.get_filters()


async def _get_optional_discogs_client() -> DiscogsClient | None:
    """Provide a DiscogsClient if settings are configured, else None.

    This allows album endpoints to function without Discogs credentials.
    Tracklist caching is simply skipped when the client is unavailable.
    """
    try:
        from cue_the_music.config import get_settings

        settings = get_settings()
        return DiscogsClient(settings)
    except Exception:
        return None


async def get_album_service(
    discogs_client: Annotated[
        DiscogsClient | None, Depends(_get_optional_discogs_client)
    ],
    repository: Annotated[AlbumRepository, Depends(get_album_repository)],
) -> AlbumService:
    """FastAPI dependency that provides an AlbumService instance."""
    return AlbumService(discogs_client=discogs_client, repository=repository)
