"""Service layer for queue, voting, and now-playing business logic.

Services orchestrate calls to repositories and contain business rules.
They never access the database session directly. The broadcaster is
optional to allow the service to work without SSE in tests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request

from cue_the_music.exceptions.exceptions import (
    AlbumNotFoundError,
    QueueItemNotFoundError,
    RequestLimitExceededError,
)
from cue_the_music.repositories.album_repository import (
    AlbumRepository,
    get_album_repository,
)
from cue_the_music.repositories.now_playing_repository import (
    NowPlayingRepository,
    get_now_playing_repository,
)
from cue_the_music.repositories.queue_repository import (
    QueueRepository,
    get_queue_repository,
)
from cue_the_music.repositories.vote_repository import (
    VoteRepository,
    get_vote_repository,
)
from cue_the_music.schemas.queue_schemas import (
    AlbumSummary,
    NowPlayingGetResponse,
    QueueItemGetResponse,
    QueueStateResponse,
    VoteGetResponse,
)

if TYPE_CHECKING:
    from cue_the_music.events.broadcaster import MessageBroadcaster

GUEST_REQUEST_LIMIT = 3


class QueueService:
    """Business logic for queue, voting, and now-playing operations."""

    def __init__(
        self,
        album_repo: AlbumRepository,
        broadcaster: MessageBroadcaster | None,
        now_playing_repo: NowPlayingRepository,
        queue_repo: QueueRepository,
        vote_repo: VoteRepository,
    ) -> None:
        self._album_repo = album_repo
        self._broadcaster = broadcaster
        self._now_playing_repo = now_playing_repo
        self._queue_repo = queue_repo
        self._vote_repo = vote_repo

    async def _broadcast(self, event_type: str, data: dict) -> None:  # type: ignore[type-arg]
        """Broadcast an event if a broadcaster is available."""
        if self._broadcaster is not None:
            await self._broadcaster.broadcast(event_type, data)

    async def request_album(self, album_id: int, ip: str) -> QueueItemGetResponse:
        """Add an album to the queue.

        Validates the album exists and the guest hasn't exceeded the request limit.
        Uses insert-and-catch for duplicate detection (not check-then-insert).
        """
        # Validate album exists
        album = await self._album_repo.get_by_id(album_id)
        if album is None:
            raise AlbumNotFoundError(album_id)

        # Check request limit
        count = await self._queue_repo.count_active_requests(ip)
        if count >= GUEST_REQUEST_LIMIT:
            raise RequestLimitExceededError(GUEST_REQUEST_LIMIT)

        # Insert (catches IntegrityError for duplicates inside the repo)
        item = await self._queue_repo.add_to_queue(album_id, ip)

        response = QueueItemGetResponse(
            id=item.id,
            album=AlbumSummary.model_validate(album),
            created_at=item.created_at,
            is_mine=True,
            requested_by_ip=item.requested_by_ip,
            votes=VoteGetResponse(up_count=0, down_count=0, my_vote=None),
        )

        await self._broadcast("queue_update", {"reason": "request_added"})
        return response

    async def cancel_request(self, queue_item_id: int, ip: str) -> None:
        """Cancel a queue request. Only the requesting IP can cancel."""
        removed = await self._queue_repo.remove_from_queue(queue_item_id, ip=ip)
        if not removed:
            raise QueueItemNotFoundError(queue_item_id)

        await self._broadcast("queue_update", {"reason": "request_cancelled"})

    async def get_queue_state(self, client_ip: str) -> QueueStateResponse:
        """Return the full queue state including now playing, queue items, and votes."""
        # Get now playing
        now_playing_row = await self._now_playing_repo.get_current()
        now_playing = None
        if now_playing_row is not None:
            now_playing = NowPlayingGetResponse(
                album=AlbumSummary.model_validate(now_playing_row.album),
                promoted_at=now_playing_row.promoted_at,
            )

        # Get queue items
        items = await self._queue_repo.get_queue_items()
        item_ids = [item.id for item in items]

        # Get vote aggregates
        vote_data = await self._queue_repo.get_vote_aggregates(item_ids, client_ip)

        # Build response
        queue_items = []
        for item in items:
            votes = vote_data.get(
                item.id, {"up_count": 0, "down_count": 0, "my_vote": None}
            )
            queue_items.append(
                QueueItemGetResponse(
                    id=item.id,
                    album=AlbumSummary.model_validate(item.album),
                    created_at=item.created_at,
                    is_mine=item.requested_by_ip == client_ip,
                    requested_by_ip=item.requested_by_ip,
                    votes=VoteGetResponse(**votes),
                )
            )

        return QueueStateResponse(
            now_playing=now_playing,
            queue=queue_items,
            count=len(queue_items),
        )

    async def cast_vote(
        self, queue_item_id: int, ip: str, value: int
    ) -> None:
        """Cast or update a vote on a queue item."""
        item = await self._queue_repo.get_queue_item(queue_item_id)
        if item is None:
            raise QueueItemNotFoundError(queue_item_id)
        await self._vote_repo.upsert_vote(queue_item_id, ip, value)
        await self._broadcast(
            "vote_update", {"queue_item_id": queue_item_id}
        )

    async def remove_vote(self, queue_item_id: int, ip: str) -> None:
        """Remove a vote from a queue item."""
        removed = await self._vote_repo.remove_vote(queue_item_id, ip)
        if not removed:
            raise QueueItemNotFoundError(queue_item_id)

        await self._broadcast(
            "vote_update", {"queue_item_id": queue_item_id}
        )

    async def promote_to_now_playing(self, queue_item_id: int) -> None:
        """Promote a queue item to now playing (atomic: delete + upsert).

        The queue item is deleted (cascading votes) and the album is set as
        now playing, all within the current transaction.
        """
        item = await self._queue_repo.get_queue_item(queue_item_id)
        if item is None:
            raise QueueItemNotFoundError(queue_item_id)

        album_id = item.album_id

        # Delete queue item (cascades votes)
        await self._queue_repo.remove_from_queue(queue_item_id)

        # Upsert now playing
        await self._now_playing_repo.upsert(album_id)

        await self._broadcast("queue_update", {"reason": "promoted"})

    async def skip_queue_item(self, queue_item_id: int) -> None:
        """Host removes any queue item regardless of ownership."""
        removed = await self._queue_repo.remove_from_queue(queue_item_id)
        if not removed:
            raise QueueItemNotFoundError(queue_item_id)

        await self._broadcast("queue_update", {"reason": "skipped"})

    async def clear_now_playing(self) -> None:
        """Clear the now-playing slot."""
        await self._now_playing_repo.clear()

        await self._broadcast("queue_update", {"reason": "now_playing_cleared"})

    async def clear_queue(self) -> None:
        """Clear all queue items and now playing."""
        await self._queue_repo.clear_all()
        await self._now_playing_repo.clear()

        await self._broadcast("queue_update", {"reason": "queue_cleared"})


async def get_queue_service(
    album_repo: Annotated[AlbumRepository, Depends(get_album_repository)],
    now_playing_repo: Annotated[
        NowPlayingRepository, Depends(get_now_playing_repository)
    ],
    queue_repo: Annotated[QueueRepository, Depends(get_queue_repository)],
    request: Request,
    vote_repo: Annotated[VoteRepository, Depends(get_vote_repository)],
) -> QueueService:
    """FastAPI dependency that provides a QueueService instance.

    The broadcaster is retrieved from app.state if available (None in tests).
    """
    broadcaster = getattr(request.app.state, "broadcaster", None)
    return QueueService(
        album_repo=album_repo,
        broadcaster=broadcaster,
        now_playing_repo=now_playing_repo,
        queue_repo=queue_repo,
        vote_repo=vote_repo,
    )
