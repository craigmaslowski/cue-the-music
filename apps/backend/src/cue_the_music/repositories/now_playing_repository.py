"""Repository for NowPlaying database queries.

All database access for the now-playing singleton is centralized here.
Services call the repository; they never touch the session directly.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.dependencies.database import get_session
from cue_the_music.models.now_playing import NowPlaying


class NowPlayingRepository:
    """Handles all NowPlaying-related database queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(self, album_id: int) -> None:
        """Insert or update the singleton now-playing row (id=1)."""
        stmt = text("""
            INSERT INTO now_playing (id, album_id, promoted_at)
            VALUES (1, :album_id, CURRENT_TIMESTAMP)
            ON CONFLICT (id)
            DO UPDATE SET album_id = :album_id, promoted_at = CURRENT_TIMESTAMP
        """)
        await self._session.execute(stmt, {"album_id": album_id})

    async def get_current(self) -> NowPlaying | None:
        """Get the current now-playing row with album info."""
        stmt = select(NowPlaying).where(NowPlaying.id == 1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def clear(self) -> bool:
        """Delete the now-playing row. Returns True if a row was deleted."""
        stmt = delete(NowPlaying)
        result = await self._session.execute(stmt)
        return result.rowcount > 0  # type: ignore[union-attr]


async def get_now_playing_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NowPlayingRepository:
    """FastAPI dependency that provides a NowPlayingRepository instance."""
    return NowPlayingRepository(session)
