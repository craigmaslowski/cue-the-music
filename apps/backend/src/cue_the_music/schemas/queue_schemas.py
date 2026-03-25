"""Pydantic schemas for Queue, Vote, and NowPlaying API endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QueueItemCreateRequest(BaseModel):
    """Request to add an album to the queue."""

    album_id: int = Field(gt=0)


class AlbumSummary(BaseModel):
    """Minimal album info embedded in queue responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    artist: str
    title: str
    cover_art_thumbnail_url: str | None
    year: int | None


class VoteGetResponse(BaseModel):
    """Vote counts and the requesting client's vote on a queue item."""

    up_count: int
    down_count: int
    my_vote: Literal[1, -1] | None


class QueueItemGetResponse(BaseModel):
    """A single queue item with album info and vote state."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    album: AlbumSummary
    requested_by_ip: str
    votes: VoteGetResponse
    created_at: datetime


class NowPlayingGetResponse(BaseModel):
    """The currently playing album."""

    model_config = ConfigDict(from_attributes=True)

    album: AlbumSummary
    promoted_at: datetime


class QueueStateResponse(BaseModel):
    """Full queue state: now playing + ordered queue items."""

    now_playing: NowPlayingGetResponse | None
    queue: list[QueueItemGetResponse]
    count: int


class VoteCastRequest(BaseModel):
    """Request to cast or change a vote."""

    value: Literal[1, -1]


class QueueItemPromoteRequest(BaseModel):
    """Request to promote a queue item to now playing."""

    queue_item_id: int = Field(gt=0)
