"""Tests for the SSE MessageBroadcaster."""

import asyncio

import pytest

from cue_the_music.events.broadcaster import MessageBroadcaster


@pytest.mark.asyncio
class TestMessageBroadcaster:
    """Tests for add/remove clients, broadcasting, and connection limits."""

    async def test_add_and_remove_client(self) -> None:
        """Adding a client returns a queue; removing cleans up."""
        broadcaster = MessageBroadcaster()
        queue = broadcaster.add_client("192.168.1.1")

        assert broadcaster.client_count == 1
        assert broadcaster.ip_count("192.168.1.1") == 1

        broadcaster.remove_client(queue)

        assert broadcaster.client_count == 0
        assert broadcaster.ip_count("192.168.1.1") == 0

    async def test_broadcast_reaches_all_clients(self) -> None:
        """A broadcast message is delivered to every connected client."""
        broadcaster = MessageBroadcaster()
        queue_a = broadcaster.add_client("192.168.1.1")
        queue_b = broadcaster.add_client("192.168.1.2")

        await broadcaster.broadcast("queue_update", {"reason": "test"})

        msg_a = queue_a.get_nowait()
        msg_b = queue_b.get_nowait()

        assert "queue_update" in msg_a
        assert "queue_update" in msg_b

        broadcaster.remove_client(queue_a)
        broadcaster.remove_client(queue_b)

    async def test_global_connection_limit(self) -> None:
        """Adding more than 50 clients raises ConnectionError."""
        broadcaster = MessageBroadcaster()
        queues = []

        for i in range(50):
            # Use unique IPs to avoid per-IP limit
            q = broadcaster.add_client(f"10.0.0.{i}")
            queues.append(q)

        with pytest.raises(ConnectionError, match="Maximum SSE connections"):
            broadcaster.add_client("10.0.1.0")

        # Clean up
        for q in queues:
            broadcaster.remove_client(q)

    async def test_per_ip_connection_limit(self) -> None:
        """Adding more than 3 clients from the same IP raises ConnectionError."""
        broadcaster = MessageBroadcaster()
        queues = []

        for _ in range(3):
            q = broadcaster.add_client("192.168.1.1")
            queues.append(q)

        with pytest.raises(ConnectionError, match="per IP"):
            broadcaster.add_client("192.168.1.1")

        for q in queues:
            broadcaster.remove_client(q)

    async def test_vote_debouncing(self) -> None:
        """Multiple vote_update events within 500ms are coalesced into one."""
        broadcaster = MessageBroadcaster()
        queue = broadcaster.add_client("192.168.1.1")

        # Fire 5 vote updates rapidly
        for i in range(5):
            await broadcaster.broadcast(
                "vote_update", {"queue_item_id": i}
            )

        # Wait for debounce window to elapse
        await asyncio.sleep(0.7)

        # Only one message should be in the queue (the last one)
        messages = []
        while not queue.empty():
            messages.append(queue.get_nowait())

        assert len(messages) == 1
        assert "vote_update" in messages[0]

        broadcaster.remove_client(queue)

    async def test_non_vote_events_not_debounced(self) -> None:
        """Non-vote events are broadcast immediately without debouncing."""
        broadcaster = MessageBroadcaster()
        queue = broadcaster.add_client("192.168.1.1")

        await broadcaster.broadcast("queue_update", {"reason": "a"})
        await broadcaster.broadcast("queue_update", {"reason": "b"})
        await broadcaster.broadcast("queue_update", {"reason": "c"})

        messages = []
        while not queue.empty():
            messages.append(queue.get_nowait())

        assert len(messages) == 3

        broadcaster.remove_client(queue)

    async def test_stale_client_removed_on_full_queue(self) -> None:
        """A client whose queue is full gets disconnected on broadcast."""
        broadcaster = MessageBroadcaster()
        queue = broadcaster.add_client("192.168.1.1")

        # Fill the queue to capacity (100 items)
        for i in range(100):
            queue.put_nowait(f"msg-{i}")

        assert queue.full()

        # Broadcasting should remove the stale client
        await broadcaster.broadcast("queue_update", {"reason": "overflow"})

        assert broadcaster.client_count == 0
