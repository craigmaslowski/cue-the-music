"""Album API endpoints.

Thin route handlers that delegate to AlbumService for business logic.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from cue_the_music.schemas.album_schemas import (
    AlbumGetResponse,
    AlbumListResponse,
)
from cue_the_music.services.album_service import AlbumService, get_album_service

router = APIRouter(prefix="/api", tags=["albums"])


@router.get("/albums", response_model=AlbumListResponse)
async def list_albums(
    service: Annotated[AlbumService, Depends(get_album_service)],
) -> AlbumListResponse:
    """List all albums in the collection."""
    albums = await service.get_albums()
    return AlbumListResponse(
        albums=[AlbumGetResponse.model_validate(a) for a in albums],
        count=len(albums),
    )


@router.get("/albums/{album_id}", response_model=AlbumGetResponse)
async def get_album(
    album_id: int,
    service: Annotated[AlbumService, Depends(get_album_service)],
) -> AlbumGetResponse:
    """Retrieve a single album by ID."""
    album = await service.get_album_detail(album_id)
    return AlbumGetResponse.model_validate(album)
