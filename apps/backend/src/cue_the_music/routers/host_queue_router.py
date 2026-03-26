"""Host queue management API endpoints.

Thin route handlers that delegate to QueueService for business logic.
All endpoints require a valid host token via the X-Host-Token header.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from cue_the_music.dependencies.host_auth import HostAuthDep
from cue_the_music.schemas.queue_schemas import QueueItemPromoteRequest
from cue_the_music.services.queue_service import QueueService, get_queue_service

router = APIRouter(prefix="/api/host", tags=["host-queue"])


@router.post("/now-playing", status_code=204)
async def promote_to_now_playing(
    _auth: HostAuthDep,
    body: QueueItemPromoteRequest,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Promote a queue item to now playing (host action)."""
    await service.promote_to_now_playing(body.queue_item_id)


@router.delete("/now-playing", status_code=204)
async def clear_now_playing(
    _auth: HostAuthDep,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Clear the currently playing album (host action)."""
    await service.clear_now_playing()


@router.delete("/queue", status_code=204)
async def clear_queue(
    _auth: HostAuthDep,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Clear all queue items and now playing (host action)."""
    await service.clear_queue()


@router.delete("/queue/{queue_item_id}", status_code=204)
async def skip_queue_item(
    _auth: HostAuthDep,
    queue_item_id: int,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Remove any queue item regardless of ownership (host action)."""
    await service.skip_queue_item(queue_item_id)
