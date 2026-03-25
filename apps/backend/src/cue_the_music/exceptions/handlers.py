"""Global exception handlers that map custom exceptions to HTTP responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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

# Map each exception to its HTTP status code
_EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    AlbumAlreadyQueuedError: 409,
    AlbumNotFoundError: 404,
    DiscogsRateLimitError: 429,
    DiscogsSyncError: 502,
    InvalidHostPinError: 401,
    QueueItemNotFoundError: 404,
    RequestLimitExceededError: 429,
    UnauthorizedHostActionError: 403,
    VoteNotFoundError: 404,
}


def _make_handler(
    status_code: int,
) -> callable:  # type: ignore[type-arg]
    """Create an exception handler that returns a JSON error with the given status."""

    async def handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            content={"detail": exc.message},  # type: ignore[attr-defined]
            status_code=status_code,
        )

    return handler


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""
    for exc_class, status_code in _EXCEPTION_STATUS_MAP.items():
        app.add_exception_handler(exc_class, _make_handler(status_code))
