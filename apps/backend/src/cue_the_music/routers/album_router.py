"""Album API endpoints.

Thin route handlers that delegate to AlbumService for business logic.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from cue_the_music.schemas.album_schemas import (
    AlbumFilterGetResponse,
    AlbumGetResponse,
    AlbumListResponse,
)
from cue_the_music.services.album_service import AlbumService, get_album_service

router = APIRouter(prefix="/api", tags=["albums"])


@router.get("/album-filters", response_model=AlbumFilterGetResponse)
async def get_album_filters(
    service: Annotated[AlbumService, Depends(get_album_service)],
) -> AlbumFilterGetResponse:
    """Return available genre and decade filter values for the collection."""
    filters = await service.get_available_filters()
    return AlbumFilterGetResponse(
        decades=filters["decades"],
        genres=filters["genres"],
    )


@router.get("/albums", response_model=AlbumListResponse)
async def list_albums(
    service: Annotated[AlbumService, Depends(get_album_service)],
    decade: Annotated[list[int] | None, Query(alias="decade")] = None,
    genre: Annotated[list[str] | None, Query(alias="genre")] = None,
    search: str | None = None,
) -> AlbumListResponse:
    """List albums with optional search, genre, and decade filters."""
    albums = await service.get_albums(
        decades=decade,
        genres=genre,
        search=search,
    )
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
