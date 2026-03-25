"""Host queue management API endpoints.

Thin route handlers that delegate to QueueService for business logic.
These endpoints are for host-only actions (auth to be added in Phase 4).
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from cue_the_music.schemas.queue_schemas import QueueItemPromoteRequest
from cue_the_music.services.queue_service import QueueService, get_queue_service

router = APIRouter(prefix="/api/host", tags=["host-queue"])


@router.post("/now-playing", status_code=204)
async def promote_to_now_playing(
    body: QueueItemPromoteRequest,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Promote a queue item to now playing (host action)."""
    await service.promote_to_now_playing(body.queue_item_id)


@router.delete("/now-playing", status_code=204)
async def clear_now_playing(
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Clear the currently playing album (host action)."""
    await service.clear_now_playing()


@router.delete("/queue/{queue_item_id}", status_code=204)
async def skip_queue_item(
    queue_item_id: int,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Remove any queue item regardless of ownership (host action)."""
    await service.skip_queue_item(queue_item_id)
