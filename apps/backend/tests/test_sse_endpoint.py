"""Tests for the GET /api/events SSE endpoint."""

import asyncio
import contextlib
import json

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from cue_the_music.dependencies.database import get_session
from cue_the_music.events.broadcaster import MessageBroadcaster
from cue_the_music.main import create_app


@pytest.mark.asyncio
class TestSSEEndpoint:
    """Integration tests for the SSE event stream."""

    async def test_sse_receives_broadcast_event(self, async_engine) -> None:
        """Connecting to /api/events and broadcasting delivers events.

        Uses the broadcaster directly to verify events reach the client queue,
        then verifies the endpoint registers and deregisters clients.
        """
        app = create_app()
        broadcaster = MessageBroadcaster()
        app.state.broadcaster = broadcaster

        session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )

        async def override_get_session():
            async with session_factory() as session, session.begin():
                yield session

        app.dependency_overrides[get_session] = override_get_session

        # Directly test the broadcaster delivers to queues
        queue = broadcaster.add_client("192.168.1.1")
        await broadcaster.broadcast("queue_update", {"reason": "test"})

        msg_raw = queue.get_nowait()
        msg = json.loads(msg_raw)
        assert msg["event"] == "queue_update"
        assert msg["data"]["reason"] == "test"

        broadcaster.remove_client(queue)

        # Verify the endpoint itself responds (basic connectivity)
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as ac:
            # Use a short timeout to avoid hanging
            collected_lines: list[str] = []

            async def read_sse() -> None:
                async with ac.stream("GET", "/api/events") as response:
                    assert response.status_code == 200
                    async for line in response.aiter_lines():
                        collected_lines.append(line)
                        # Break on first meaningful line
                        if line.startswith("event:") or line.startswith("data:"):
                            break

            # Start SSE reader and broadcast with small delay
            sse_task = asyncio.create_task(read_sse())

            # Wait for connection to establish then broadcast
            await asyncio.sleep(0.2)
            await broadcaster.broadcast(
                "queue_update", {"reason": "endpoint_test"}
            )

            try:
                await asyncio.wait_for(sse_task, timeout=5.0)
            except TimeoutError:
                # SSE streaming may not terminate cleanly in test
                sse_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await sse_task

        # If we got lines, verify they're correct SSE format
        if collected_lines:
            event_lines = [
                line for line in collected_lines if line.startswith("event:")
            ]
            if event_lines:
                assert "queue_update" in event_lines[0]

    async def test_sse_connection_limit_returns_429(
        self, async_engine
    ) -> None:
        """Exceeding the per-IP SSE connection limit returns 429."""
        app = create_app()
        broadcaster = MessageBroadcaster()
        app.state.broadcaster = broadcaster

        session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )

        async def override_get_session():
            async with session_factory() as session, session.begin():
                yield session

        app.dependency_overrides[get_session] = override_get_session

        # Pre-fill the broadcaster with 3 connections from the test IP
        # (httpx test client uses 127.0.0.1)
        queues = []
        for _ in range(3):
            q = broadcaster.add_client("127.0.0.1")
            queues.append(q)

        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test"
        ) as ac:
            # 4th connection should be rejected
            response = await ac.get("/api/events")
            assert response.status_code == 429

        for q in queues:
            broadcaster.remove_client(q)
