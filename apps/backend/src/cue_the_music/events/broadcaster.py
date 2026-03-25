"""Server-Sent Events broadcaster with queue-per-client pattern.

The MessageBroadcaster is a singleton created during the FastAPI lifespan
and stored on app.state. It manages per-client asyncio queues, enforces
connection limits, and debounces vote_update events to cap the refetch
storm at 2 events/second regardless of vote velocity.
"""

import asyncio
import contextlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Connection limits
_MAX_CLIENTS = 50
_MAX_CLIENTS_PER_IP = 3
_MAX_QUEUE_DEPTH = 100

# Vote debounce window in seconds
_VOTE_DEBOUNCE_SECONDS = 0.5


class MessageBroadcaster:
    """Manages SSE client connections and broadcasts events.

    Each connected client gets an asyncio.Queue. Events are broadcast by
    putting serialized SSE data onto every client queue. Stale clients
    (queue full) are automatically removed.
    """

    def __init__(self) -> None:
        # Map of queue -> client IP for tracking per-IP limits
        self._clients: dict[asyncio.Queue[str | None], str] = {}

        # Per-IP connection count
        self._ip_counts: dict[str, int] = {}

        # Vote debouncing state
        self._vote_debounce_task: asyncio.Task[None] | None = None
        self._vote_debounce_data: dict[str, Any] | None = None

    @property
    def client_count(self) -> int:
        """Total number of connected SSE clients."""
        return len(self._clients)

    def ip_count(self, ip: str) -> int:
        """Number of active connections from a specific IP."""
        return self._ip_counts.get(ip, 0)

    def add_client(self, ip: str) -> asyncio.Queue[str | None]:
        """Register a new SSE client and return its message queue.

        Enforces global and per-IP connection limits. Raises ConnectionError
        if limits are exceeded.
        """
        if len(self._clients) >= _MAX_CLIENTS:
            raise ConnectionError(
                f"Maximum SSE connections ({_MAX_CLIENTS}) reached."
            )

        current_ip_count = self._ip_counts.get(ip, 0)
        if current_ip_count >= _MAX_CLIENTS_PER_IP:
            raise ConnectionError(
                f"Maximum connections per IP ({_MAX_CLIENTS_PER_IP}) reached."
            )

        queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=_MAX_QUEUE_DEPTH)
        self._clients[queue] = ip
        self._ip_counts[ip] = current_ip_count + 1

        logger.info(
            "SSE client connected (ip=%s, total=%d)",
            ip,
            len(self._clients),
        )
        return queue

    def remove_client(self, queue: asyncio.Queue[str | None]) -> None:
        """Unregister an SSE client and clean up its tracking state."""
        ip = self._clients.pop(queue, None)
        if ip is not None:
            self._ip_counts[ip] = max(0, self._ip_counts.get(ip, 1) - 1)
            if self._ip_counts[ip] == 0:
                del self._ip_counts[ip]
            logger.info(
                "SSE client disconnected (ip=%s, total=%d)",
                ip,
                len(self._clients),
            )

    async def broadcast(self, event_type: str, data: dict[str, Any]) -> None:
        """Broadcast an event to all connected clients.

        For vote_update events, the broadcast is debounced — multiple vote
        changes within a 500ms window are coalesced into a single broadcast.
        Other event types are broadcast immediately.
        """
        if event_type == "vote_update":
            await self._debounced_vote_broadcast(data)
        else:
            await self._send_to_all(event_type, data)

    async def _debounced_vote_broadcast(self, data: dict[str, Any]) -> None:
        """Debounce vote_update events within a 500ms window.

        If another vote_update arrives before the timer fires, the timer
        resets and the latest data is used for the broadcast.
        """
        self._vote_debounce_data = data

        # Cancel any pending debounce timer
        if self._vote_debounce_task is not None and not self._vote_debounce_task.done():
            self._vote_debounce_task.cancel()

        self._vote_debounce_task = asyncio.create_task(
            self._fire_debounced_vote()
        )

    async def _fire_debounced_vote(self) -> None:
        """Wait for the debounce window then broadcast the latest vote data."""
        await asyncio.sleep(_VOTE_DEBOUNCE_SECONDS)
        if self._vote_debounce_data is not None:
            data = self._vote_debounce_data
            self._vote_debounce_data = None
            await self._send_to_all("vote_update", data)

    async def _send_to_all(
        self, event_type: str, data: dict[str, Any]
    ) -> None:
        """Put a serialized SSE message onto every client queue.

        Clients whose queues are full (>100 items) are disconnected by
        sending None (poison pill) and removing them.
        """
        message = json.dumps({"event": event_type, "data": data})
        stale_clients: list[asyncio.Queue[str | None]] = []

        for queue in list(self._clients.keys()):
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                # Client is too slow — mark for removal
                logger.warning(
                    "SSE client queue full, disconnecting (ip=%s)",
                    self._clients.get(queue, "unknown"),
                )
                stale_clients.append(queue)

        # Clean up stale clients
        for queue in stale_clients:
            # Send None as poison pill to signal disconnect
            with contextlib.suppress(asyncio.QueueFull):
                queue.put_nowait(None)
            self.remove_client(queue)
