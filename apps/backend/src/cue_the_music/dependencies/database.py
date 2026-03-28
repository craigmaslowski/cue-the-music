"""Async SQLAlchemy engine and session management for SQLite."""

import os
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Async engine with aiosqlite driver — configurable via DATABASE_URL env var
_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "sqlite+aiosqlite:///./cue_the_music.db"
)

engine = create_async_engine(
    _DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Session factory with expire_on_commit=False to allow access after commit
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragmas(dbapi_connection: object, _connection_record: object) -> None:
    """Configure SQLite PRAGMAs for performance and correctness on each connection."""
    cursor = dbapi_connection.cursor()  # type: ignore[union-attr]
    cursor.execute("PRAGMA busy_timeout = 5000")
    cursor.execute("PRAGMA cache_size = -64000")
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.close()


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Yield an async session per request, with automatic cleanup."""
    async with async_session_factory() as session, session.begin():
        yield session


# Annotated type alias for use in Depends()
SessionDep = Annotated[AsyncSession, Depends(get_session)]
