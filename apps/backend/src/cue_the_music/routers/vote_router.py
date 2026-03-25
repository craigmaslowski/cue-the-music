"""Vote API endpoints for guests.

Thin route handlers that delegate to QueueService for business logic.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from cue_the_music.schemas.queue_schemas import VoteCastRequest
from cue_the_music.services.queue_service import QueueService, get_queue_service

router = APIRouter(prefix="/api", tags=["votes"])


@router.put("/queue/{queue_item_id}/vote", status_code=204)
async def cast_vote(
    request: Request,
    queue_item_id: int,
    body: VoteCastRequest,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Cast or update a vote on a queue item."""
    client_ip = request.client.host  # type: ignore[union-attr]
    await service.cast_vote(queue_item_id, client_ip, body.value)


@router.delete("/queue/{queue_item_id}/vote", status_code=204)
async def remove_vote(
    request: Request,
    queue_item_id: int,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Remove a vote from a queue item."""
    client_ip = request.client.host  # type: ignore[union-attr]
    await service.remove_vote(queue_item_id, client_ip)
