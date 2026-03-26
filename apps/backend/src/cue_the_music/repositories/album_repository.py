"""Repository for Album database queries.

All database access for albums is centralized here. Services call the
repository; they never touch the session directly.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.dependencies.database import get_session
from cue_the_music.models.album import Album


class AlbumRepository:
    """Handles all Album-related database queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[Album]:
        """Retrieve all albums ordered by artist then title."""
        stmt = select(Album).order_by(Album.artist, Album.title)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, album_id: int) -> Album | None:
        """Retrieve a single album by its primary key."""
        stmt = select(Album).where(Album.id == album_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_tracklist(
        self, album_id: int, tracklist: list[dict[str, str]]
    ) -> Album | None:
        """Store a fetched tracklist on an existing album.

        Args:
            album_id: Primary key of the album to update.
            tracklist: List of track dicts (position, title, duration).

        Returns:
            The updated Album, or None if not found.
        """
        album = await self._session.get(Album, album_id)
        if album is None:
            return None
        album.tracklist = tracklist
        await self._session.flush()
        await self._session.refresh(album)
        return album


async def get_album_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AlbumRepository:
    """FastAPI dependency that provides an AlbumRepository instance."""
    return AlbumRepository(session)
