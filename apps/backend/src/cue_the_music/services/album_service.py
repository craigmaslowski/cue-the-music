"""Service layer for album business logic.

Services orchestrate calls to repositories and contain business rules.
They never access the database session directly.
"""

from typing import Annotated

from fastapi import Depends

from cue_the_music.exceptions.exceptions import AlbumNotFoundError
from cue_the_music.models.album import Album
from cue_the_music.repositories.album_repository import (
    AlbumRepository,
    get_album_repository,
)


class AlbumService:
    """Business logic for album operations."""

    def __init__(self, repository: AlbumRepository) -> None:
        self._repository = repository

    async def get_album_detail(self, album_id: int) -> Album:
        """Retrieve a single album by ID, raising if not found.

        Future enhancement: handle tracklist caching from Discogs API.
        """
        album = await self._repository.get_by_id(album_id)
        if album is None:
            raise AlbumNotFoundError(album_id)
        return album

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


async def get_album_service(
    repository: Annotated[AlbumRepository, Depends(get_album_repository)],
) -> AlbumService:
    """FastAPI dependency that provides an AlbumService instance."""
    return AlbumService(repository)
