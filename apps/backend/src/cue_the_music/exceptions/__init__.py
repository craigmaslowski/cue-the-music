"""Custom exception classes and global exception handler."""

from cue_the_music.exceptions.exceptions import (
    AlbumAlreadyQueuedError,
    AlbumNotFoundError,
    DiscogsRateLimitError,
    DiscogsSyncError,
    InvalidHostPinError,
    QueueItemNotFoundError,
    RequestLimitExceededError,
    UnauthorizedHostActionError,
    VoteNotFoundError,
)
from cue_the_music.exceptions.handlers import register_exception_handlers
from cue_the_music.exceptions.rate_limit import PinRateLimitExceededError

__all__ = [
    "AlbumAlreadyQueuedError",
    "AlbumNotFoundError",
    "DiscogsRateLimitError",
    "DiscogsSyncError",
    "InvalidHostPinError",
    "PinRateLimitExceededError",
    "QueueItemNotFoundError",
    "RequestLimitExceededError",
    "UnauthorizedHostActionError",
    "VoteNotFoundError",
    "register_exception_handlers",
]
