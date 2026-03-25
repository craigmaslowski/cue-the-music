"""Pydantic schemas for Discogs collection sync endpoints."""

from pydantic import BaseModel


class CollectionSyncStatusResponse(BaseModel):
    """Response schema for sync status queries."""

    albums_synced: int
    in_progress: bool
    total_pages: int


class CollectionSyncTriggerResponse(BaseModel):
    """Response schema for triggering a collection sync."""

    albums_synced: int
    status: str
