"""FastAPI application factory and lifespan handler."""

import asyncio
import contextlib
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from cue_the_music.events.broadcaster import MessageBroadcaster
from cue_the_music.exceptions.handlers import register_exception_handlers
from cue_the_music.routers.album_router import router as album_router
from cue_the_music.routers.host_auth_router import router as host_auth_router
from cue_the_music.routers.host_queue_router import router as host_queue_router
from cue_the_music.routers.queue_router import router as queue_router
from cue_the_music.routers.sse_router import router as sse_router
from cue_the_music.routers.sync_router import router as sync_router
from cue_the_music.routers.vote_router import router as vote_router

logger = logging.getLogger(__name__)


async def _heartbeat_loop(broadcaster: MessageBroadcaster) -> None:
    """Background task that broadcasts heartbeat events every 30 seconds.

    Runs until cancelled during shutdown. The heartbeat keeps SSE
    connections alive and helps detect dead clients.
    """
    while True:
        await asyncio.sleep(30)
        await broadcaster.broadcast("heartbeat", {})


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan handler for startup and shutdown tasks."""
    from cue_the_music.dependencies.database import engine

    # Startup: clear ephemeral queue state (queue resets on server restart)
    # Tables may not exist yet if migrations haven't run — skip silently
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DELETE FROM votes"))
            await conn.execute(text("DELETE FROM queue_items"))
            await conn.execute(text("DELETE FROM now_playing"))
        logger.info("Cleared queue, votes, and now-playing on startup.")
    except Exception:
        logger.warning("Could not clear ephemeral tables — run Alembic migrations first.")

    # Create the SSE broadcaster singleton and store on app.state
    broadcaster = MessageBroadcaster()
    app.state.broadcaster = broadcaster

    # Start heartbeat background task
    heartbeat_task = asyncio.create_task(_heartbeat_loop(broadcaster))

    yield

    # Shutdown: cancel heartbeat and dispose engine
    heartbeat_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await heartbeat_task

    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        lifespan=lifespan,
        title="Cue the Music",
        version="0.1.0",
    )

    # CORS middleware for local development
    app.add_middleware(
        CORSMiddleware,
        allow_headers=["*"],
        allow_methods=["*"],
        allow_origins=[
            "http://localhost:4200",
            "http://localhost:5173",
        ],
    )

    # Register custom exception handlers
    register_exception_handlers(app)

    # Register routers (alphabetical)
    app.include_router(album_router)
    app.include_router(host_auth_router)
    app.include_router(host_queue_router)
    app.include_router(queue_router)
    app.include_router(sse_router)
    app.include_router(sync_router)
    app.include_router(vote_router)

    return app


# Application instance used by uvicorn
app = create_app()
