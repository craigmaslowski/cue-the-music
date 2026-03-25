"""Pydantic schemas for Album API endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlbumGetResponse(BaseModel):
    """Response schema for a single album with all fields."""

    model_config = ConfigDict(from_attributes=True)

    artist: str
    cover_art_thumbnail_url: str | None
    cover_art_url: str | None
    created_at: datetime
    discogs_release_id: str
    genre_tags: list[str] | None
    id: int
    label: str | None
    style_tags: list[str] | None
    title: str
    tracklist: list[dict[str, str]] | None
    updated_at: datetime
    year: int | None


class AlbumListResponse(BaseModel):
    """Response schema for a list of albums."""

    albums: list[AlbumGetResponse]
    count: int


class AlbumFilterGetResponse(BaseModel):
    """Response schema for available filter values (genres and decades)."""

    decades: list[int]
    genres: list[str]
