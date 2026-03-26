"""Host sync API endpoint for triggering Discogs collection sync.

Requires a valid host token via the X-Host-Token header.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from cue_the_music.dependencies.host_auth import HostAuthDep
from cue_the_music.events.broadcaster import MessageBroadcaster
from cue_the_music.schemas.sync_schemas import CollectionSyncTriggerResponse
from cue_the_music.services.sync_service import SyncService, get_sync_service

router = APIRouter(prefix="/api/host", tags=["host"])


@router.post("/sync", response_model=CollectionSyncTriggerResponse)
async def trigger_sync(
    _auth: HostAuthDep,
    request: Request,
    service: Annotated[SyncService, Depends(get_sync_service)],
) -> CollectionSyncTriggerResponse:
    """Trigger a full Discogs collection sync.

    Fetches all pages of the host's collection and upserts albums.
    Requires host authentication. Broadcasts collection_sync event on success.
    """
    result = await service.sync_collection()

    # Broadcast sync completion to all connected SSE clients
    broadcaster: MessageBroadcaster | None = getattr(
        request.app.state, "broadcaster", None
    )
    if broadcaster is not None:
        await broadcaster.broadcast(
            "collection_sync",
            {"album_count": result.albums_synced, "status": "complete"},
        )

    return CollectionSyncTriggerResponse(
        albums_synced=result.albums_synced,
        status="complete",
    )
