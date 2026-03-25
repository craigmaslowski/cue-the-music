"""FastAPI application factory and lifespan handler."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from cue_the_music.exceptions.handlers import register_exception_handlers
from cue_the_music.routers.album_router import router as album_router
from cue_the_music.routers.host_queue_router import router as host_queue_router
from cue_the_music.routers.queue_router import router as queue_router
from cue_the_music.routers.sync_router import router as sync_router
from cue_the_music.routers.vote_router import router as vote_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan handler for startup and shutdown tasks."""
    from cue_the_music.dependencies.database import engine

    # Startup: clear ephemeral queue state (queue resets on server restart)
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM votes"))
        await conn.execute(text("DELETE FROM queue_items"))
        await conn.execute(text("DELETE FROM now_playing"))
    logger.info("Cleared queue, votes, and now-playing on startup.")

    yield

    # Shutdown: dispose of the engine to release connections
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

    # Register routers
    app.include_router(album_router)
    app.include_router(sync_router)
    app.include_router(queue_router)
    app.include_router(vote_router)
    app.include_router(host_queue_router)

    return app


# Application instance used by uvicorn
app = create_app()
