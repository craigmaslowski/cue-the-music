"""Repository for QueueItem database queries.

All database access for queue items is centralized here. Services call the
repository; they never touch the session directly.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import case, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cue_the_music.dependencies.database import get_session
from cue_the_music.exceptions.exceptions import AlbumAlreadyQueuedError
from cue_the_music.models.queue_item import QueueItem
from cue_the_music.models.vote import Vote
from cue_the_music.models.vote_direction import VoteDirection


class QueueRepository:
    """Handles all QueueItem-related database queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_to_queue(self, album_id: int, ip: str) -> QueueItem:
        """Insert a new queue item. Raises AlbumAlreadyQueuedError on duplicate."""
        item = QueueItem(album_id=album_id, requested_by_ip=ip)
        self._session.add(item)
        try:
            await self._session.flush()
        except IntegrityError as err:
            await self._session.rollback()
            raise AlbumAlreadyQueuedError(album_id) from err
        return item

    async def remove_from_queue(
        self, queue_item_id: int, ip: str | None = None
    ) -> bool:
        """Delete a queue item by ID. Optionally check IP ownership.

        Returns True if a row was deleted, False otherwise.
        """
        stmt = delete(QueueItem).where(QueueItem.id == queue_item_id)
        if ip is not None:
            stmt = stmt.where(QueueItem.requested_by_ip == ip)
        result = await self._session.execute(stmt)
        return result.rowcount > 0  # type: ignore[union-attr]

    async def get_queue_items(self) -> list[QueueItem]:
        """Return all queue items ordered by insertion order (id)."""
        stmt = (
            select(QueueItem)
            .order_by(QueueItem.id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_vote_aggregates(
        self, queue_item_ids: list[int], client_ip: str
    ) -> dict[int, dict]:
        """Return vote counts and my_vote for a list of queue item IDs.

        Returns a dict keyed by queue_item_id with up_count, down_count, my_vote.
        """
        if not queue_item_ids:
            return {}

        # Aggregate up/down counts
        count_stmt = (
            select(
                Vote.queue_item_id,
                func.sum(
                    case(
                        (Vote.value == VoteDirection.UP, 1),
                        else_=0,
                    )
                ).label("up_count"),
                func.sum(
                    case(
                        (Vote.value == VoteDirection.DOWN, 1),
                        else_=0,
                    )
                ).label("down_count"),
            )
            .where(Vote.queue_item_id.in_(queue_item_ids))
            .group_by(Vote.queue_item_id)
        )
        count_result = await self._session.execute(count_stmt)
        counts = {
            row.queue_item_id: {
                "up_count": int(row.up_count or 0),
                "down_count": int(row.down_count or 0),
            }
            for row in count_result.all()
        }

        # Get my_vote for each queue item
        my_vote_stmt = (
            select(Vote.queue_item_id, Vote.value)
            .where(Vote.queue_item_id.in_(queue_item_ids))
            .where(Vote.voter_ip == client_ip)
        )
        my_vote_result = await self._session.execute(my_vote_stmt)
        my_votes = {row.queue_item_id: row.value for row in my_vote_result.all()}

        # Merge into a single dict
        aggregates: dict[int, dict] = {}
        for qid in queue_item_ids:
            item_counts = counts.get(qid, {"up_count": 0, "down_count": 0})
            aggregates[qid] = {
                **item_counts,
                "my_vote": my_votes.get(qid),
            }
        return aggregates

    async def count_active_requests(self, ip: str) -> int:
        """Count how many queue items belong to the given IP."""
        stmt = select(func.count()).select_from(QueueItem).where(
            QueueItem.requested_by_ip == ip
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_queue_item(self, queue_item_id: int) -> QueueItem | None:
        """Get a single queue item by ID."""
        return await self._session.get(QueueItem, queue_item_id)


async def get_queue_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QueueRepository:
    """FastAPI dependency that provides a QueueRepository instance."""
    return QueueRepository(session)
