"""SSE endpoint for real-time event streaming to clients.

Clients connect to GET /api/events and receive named events (queue_update,
vote_update, collection_sync, heartbeat) via Server-Sent Events.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from cue_the_music.dependencies.broadcaster import get_broadcaster
from cue_the_music.events.broadcaster import MessageBroadcaster

logger = logging.getLogger(__name__)

# Heartbeat interval in seconds
_HEARTBEAT_INTERVAL = 30

router = APIRouter(prefix="/api", tags=["events"])


async def _event_generator(
    request: Request,
    queue: asyncio.Queue[str | None],
) -> AsyncGenerator[dict[str, str]]:
    """Async generator that yields SSE events from the client's queue.

    Sends a heartbeat comment every 30 seconds if no other event arrives.
    Exits when the client disconnects or receives a poison pill (None).
    """
    try:
        while True:
            # Check for client disconnect
            if await request.is_disconnected():
                break

            try:
                # Wait for an event with a timeout for heartbeat
                message = await asyncio.wait_for(
                    queue.get(), timeout=_HEARTBEAT_INTERVAL
                )
            except TimeoutError:
                # No event within the heartbeat window — send heartbeat
                yield {"event": "heartbeat", "data": "{}"}
                continue

            # None is the poison pill — client should disconnect
            if message is None:
                break

            # Parse the message to extract event type and data
            parsed = json.loads(message)
            yield {
                "event": parsed["event"],
                "data": json.dumps(parsed["data"]),
            }
    except asyncio.CancelledError:
        # Client disconnected during iteration
        pass


@router.get("/events")
async def event_stream(
    request: Request,
    broadcaster: Annotated[MessageBroadcaster, Depends(get_broadcaster)],
) -> EventSourceResponse:
    """SSE endpoint for real-time event streaming.

    Each connected client gets a dedicated message queue. Events are
    pushed by the broadcaster when queue/vote/sync state changes.
    Connection limits are enforced (50 global, 3 per IP).
    """
    client_ip = request.client.host  # type: ignore[union-attr]

    try:
        queue = broadcaster.add_client(client_ip)
    except ConnectionError as exc:
        # Return a 429 if connection limits are exceeded
        from fastapi.responses import JSONResponse

        return JSONResponse(  # type: ignore[return-value]
            content={"detail": str(exc)},
            status_code=429,
        )

    async def generator() -> AsyncGenerator[dict[str, str]]:
        try:
            async for event in _event_generator(request, queue):
                yield event
        finally:
            broadcaster.remove_client(queue)

    return EventSourceResponse(generator())
