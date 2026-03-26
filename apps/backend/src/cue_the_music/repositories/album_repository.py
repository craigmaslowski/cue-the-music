"""Repository for Album database queries.

All database access for albums is centralized here. Services call the
repository; they never touch the session directly.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.dependencies.database import get_session
from cue_the_music.models.album import Album


class AlbumRepository:
    """Handles all Album-related database queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(
        self,
        decades: list[int] | None = None,
        genres: list[str] | None = None,
        search: str | None = None,
    ) -> list[Album]:
        """Retrieve albums with optional search and filter criteria.

        Args:
            decades: Filter by decade (e.g., [1970, 1980]
                matches years 1970-1979, 1980-1989).
            genres: Filter by genre/style tags using SQLite json_each().
            search: Case-insensitive LIKE search across artist and title.
        """
        stmt = select(Album)

        # Text search across artist and title
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                Album.artist.ilike(search_term) | Album.title.ilike(search_term)
            )

        # Genre/style filter using json_each() to search within JSON arrays
        if genres:
            genre_conditions = []
            for i, genre in enumerate(genres):
                param_name = f"genre_{i}"
                genre_conditions.append(
                    text(
                        f"""(
                            EXISTS (
                                SELECT 1 FROM json_each(albums.genre_tags)
                                WHERE json_each.value = :{param_name}
                            )
                            OR EXISTS (
                                SELECT 1 FROM json_each(albums.style_tags)
                                WHERE json_each.value = :{param_name}
                            )
                        )"""
                    ).bindparams(**{param_name: genre})
                )
            for condition in genre_conditions:
                stmt = stmt.where(condition)

        # Decade filter: match year ranges (e.g., 1970 matches 1970-1979)
        if decades:
            decade_conditions = []
            for decade in decades:
                decade_conditions.append(
                    (Album.year >= decade) & (Album.year < decade + 10)
                )
            # OR across decades (album matches if it falls in any selected decade)
            stmt = stmt.where(
                decade_conditions[0]
                if len(decade_conditions) == 1
                else decade_conditions[0] | decade_conditions[1]
                if len(decade_conditions) == 2
                else Album.year.in_(
                    [
                        y
                        for d in decades
                        for y in range(d, d + 10)
                    ]
                )
            )

        stmt = stmt.order_by(Album.artist, Album.title)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, album_id: int) -> Album | None:
        """Retrieve a single album by its primary key."""
        stmt = select(Album).where(Album.id == album_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_filters(self) -> dict[str, list]:
        """Extract unique genres and decades from the collection.

        Returns a dict with 'genres' (sorted unique genre + style tags)
        and 'decades' (sorted unique decades derived from album years).
        """
        # Extract unique genres from genre_tags and style_tags JSON arrays
        genre_result = await self._session.execute(
            text("""
                SELECT DISTINCT value FROM (
                    SELECT json_each.value
                    FROM albums, json_each(albums.genre_tags)
                    UNION
                    SELECT json_each.value
                    FROM albums, json_each(albums.style_tags)
                )
                ORDER BY value
            """)
        )
        genres = [row[0] for row in genre_result.fetchall()]

        # Extract unique decades from album years
        decade_result = await self._session.execute(
            text("""
                SELECT DISTINCT (year / 10) * 10 AS decade
                FROM albums
                WHERE year IS NOT NULL
                ORDER BY decade
            """)
        )
        decades = [row[0] for row in decade_result.fetchall()]

        return {"decades": decades, "genres": genres}


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
