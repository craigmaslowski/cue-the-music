"""FastAPI application factory and lifespan handler."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cue_the_music.exceptions.handlers import register_exception_handlers
from cue_the_music.routers.album_router import router as album_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan handler for startup and shutdown tasks."""
    # Startup: engine is created at module level in database.py
    yield
    # Shutdown: dispose of the engine to release connections
    from cue_the_music.dependencies.database import engine

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

    return app


# Application instance used by uvicorn
app = create_app()
