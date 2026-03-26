"""Queue API endpoints for guests.

Thin route handlers that delegate to QueueService for business logic.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from cue_the_music.schemas.queue_schemas import (
    QueueItemCreateRequest,
    QueueItemGetResponse,
    QueueStateResponse,
)
from cue_the_music.services.queue_service import QueueService, get_queue_service

router = APIRouter(prefix="/api", tags=["queue"])


@router.get("/queue", response_model=QueueStateResponse)
async def get_queue(
    request: Request,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> QueueStateResponse:
    """Return the full queue state including now playing and vote info."""
    client_ip = request.client.host  # type: ignore[union-attr]
    return await service.get_queue_state(client_ip)


@router.post(
    "/queue", response_model=QueueItemGetResponse, status_code=201
)
async def add_to_queue(
    request: Request,
    body: QueueItemCreateRequest,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> QueueItemGetResponse:
    """Add an album to the queue."""
    client_ip = request.client.host  # type: ignore[union-attr]
    return await service.request_album(body.album_id, client_ip)


@router.delete("/queue/{queue_item_id}", status_code=204)
async def remove_from_queue(
    request: Request,
    queue_item_id: int,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Cancel a queue request (only the requester can cancel)."""
    client_ip = request.client.host  # type: ignore[union-attr]
    await service.cancel_request(queue_item_id, client_ip)
