"""Shared test fixtures for the Cue the Music backend."""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from cue_the_music.dependencies.database import get_session
from cue_the_music.main import create_app
from cue_the_music.models.base import Base


@pytest_asyncio.fixture
async def async_engine():
    """Create an in-memory SQLite engine for tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    """Provide a transactional async session for tests."""
    session_factory = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(async_engine):
    """Provide an httpx AsyncClient wired to the FastAPI app with test DB."""
    app = create_app()

    # Override the get_session dependency to use the test database
    session_factory = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
    )

    async def override_get_session():
        async with session_factory() as session, session.begin():
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
