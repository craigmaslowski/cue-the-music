"""Shared test fixtures for the Cue the Music backend."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from cue_the_music.dependencies.database import get_session
from cue_the_music.events.broadcaster import MessageBroadcaster
from cue_the_music.main import create_app
from cue_the_music.models.base import Base
from cue_the_music.services.album_service import _get_optional_discogs_client

# Default test PIN used by the Settings fixture
TEST_HOST_PIN = "1234"


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset the Discogs rate limiter between tests to avoid cross-loop reuse."""
    import cue_the_music.integrations.discogs_client as discogs_module

    discogs_module._rate_limiter = None
    yield
    discogs_module._rate_limiter = None


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
    """Provide an httpx AsyncClient wired to the FastAPI app with test DB.

    A MessageBroadcaster is attached to app.state for SSE-related tests.
    Resets the HostAuthService singleton to avoid rate-limit state leaking.
    """
    import cue_the_music.services.host_auth_service as auth_module

    # Reset the singleton so each test starts with fresh rate-limit state
    auth_module._host_auth_service = None

    app = create_app()

    # Attach a broadcaster so QueueService can broadcast in tests
    app.state.broadcaster = MessageBroadcaster()

    # Override the get_session dependency to use the test database
    session_factory = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
    )

    async def override_get_session():
        async with session_factory() as session, session.begin():
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # Disable Discogs client in tests to prevent real HTTP calls
    # and avoid lazy-load issues after tracklist caching
    async def override_discogs_client():
        return None

    app.dependency_overrides[_get_optional_discogs_client] = override_discogs_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def get_host_token(client: AsyncClient) -> str:
    """Helper to verify the test PIN and return a host token.

    Uses the default test PIN (1234). Requires HOST_PIN=1234 env var or
    monkeypatch to be set in the test environment.
    """
    response = await client.post(
        "/api/host/verify-pin", json={"pin": TEST_HOST_PIN}
    )
    assert response.status_code == 200
    return response.json()["token"]
