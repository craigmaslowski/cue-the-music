"""Repository for Vote database queries.

All database access for votes is centralized here. Services call the
repository; they never touch the session directly.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.dependencies.database import get_session
from cue_the_music.models.vote import Vote


class VoteRepository:
    """Handles all Vote-related database queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_vote(
        self, queue_item_id: int, ip: str, value: int
    ) -> None:
        """Insert or update a vote using ON CONFLICT DO UPDATE."""
        stmt = text("""
            INSERT INTO votes (queue_item_id, voter_ip, value)
            VALUES (:queue_item_id, :voter_ip, :value)
            ON CONFLICT (queue_item_id, voter_ip)
            DO UPDATE SET value = :value
        """)
        await self._session.execute(
            stmt,
            {"queue_item_id": queue_item_id, "voter_ip": ip, "value": value},
        )

    async def remove_vote(self, queue_item_id: int, ip: str) -> bool:
        """Delete a vote. Returns True if a row was deleted."""
        stmt = (
            delete(Vote)
            .where(Vote.queue_item_id == queue_item_id)
            .where(Vote.voter_ip == ip)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0  # type: ignore[union-attr]


async def get_vote_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VoteRepository:
    """FastAPI dependency that provides a VoteRepository instance."""
    return VoteRepository(session)
