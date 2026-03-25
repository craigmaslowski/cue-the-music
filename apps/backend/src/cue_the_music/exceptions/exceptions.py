"""Custom exception classes for the Cue the Music application.

Each exception maps to a specific HTTP status code and carries a user-friendly
message suitable for display in the frontend.
"""


class AlbumAlreadyQueuedError(Exception):
    """Raised when an album is already in the queue (409 Conflict)."""

    def __init__(self, album_id: int) -> None:
        self.album_id = album_id
        self.message = "This album is already in the queue."
        super().__init__(self.message)


class AlbumNotFoundError(Exception):
    """Raised when a requested album does not exist (404 Not Found)."""

    def __init__(self, album_id: int) -> None:
        self.album_id = album_id
        self.message = "Album not found."
        super().__init__(self.message)


class DiscogsRateLimitError(Exception):
    """Raised when the Discogs API rate limit is exceeded (429 Too Many Requests)."""

    def __init__(self) -> None:
        self.message = "Discogs rate limit exceeded. Please try again later."
        super().__init__(self.message)


class DiscogsSyncError(Exception):
    """Raised when a Discogs sync operation fails (502 Bad Gateway)."""

    def __init__(self, detail: str = "") -> None:
        self.detail = detail
        self.message = "Failed to sync with Discogs. Please try again."
        super().__init__(self.message)


class InvalidHostPinError(Exception):
    """Raised when an incorrect host PIN is provided (401 Unauthorized)."""

    def __init__(self) -> None:
        self.message = "Invalid host PIN."
        super().__init__(self.message)


class QueueItemNotFoundError(Exception):
    """Raised when a requested queue item does not exist (404 Not Found)."""

    def __init__(self, queue_item_id: int) -> None:
        self.queue_item_id = queue_item_id
        self.message = "Queue item not found."
        super().__init__(self.message)


class RequestLimitExceededError(Exception):
    """Raised when a guest exceeds the request limit (429 Too Many Requests)."""

    def __init__(self, limit: int = 3) -> None:
        self.limit = limit
        self.message = f"You can only have {limit} albums in the queue at a time."
        super().__init__(self.message)


class UnauthorizedHostActionError(Exception):
    """Raised when a non-host tries a host-only action (403 Forbidden)."""

    def __init__(self) -> None:
        self.message = "Host authorization required for this action."
        super().__init__(self.message)


class VoteNotFoundError(Exception):
    """Raised when a requested vote does not exist (404 Not Found)."""

    def __init__(self, vote_id: int) -> None:
        self.vote_id = vote_id
        self.message = "Vote not found."
        super().__init__(self.message)
