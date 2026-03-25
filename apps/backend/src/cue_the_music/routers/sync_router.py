"""Host sync API endpoint for triggering Discogs collection sync.

Host auth will be added in Phase 4; for now the endpoint exists unprotected.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from cue_the_music.schemas.sync_schemas import CollectionSyncTriggerResponse
from cue_the_music.services.sync_service import SyncService, get_sync_service

router = APIRouter(prefix="/api/host", tags=["host"])


@router.post("/sync", response_model=CollectionSyncTriggerResponse)
async def trigger_sync(
    service: Annotated[SyncService, Depends(get_sync_service)],
) -> CollectionSyncTriggerResponse:
    """Trigger a full Discogs collection sync.

    Fetches all pages of the host's collection and upserts albums.
    Note: Host PIN auth will be enforced in Phase 4.
    """
    result = await service.sync_collection()
    return CollectionSyncTriggerResponse(
        albums_synced=result.albums_synced,
        status="complete",
    )
