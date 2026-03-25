"""Tests for the POST /api/host/sync endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from cue_the_music.config import Settings, get_settings
from cue_the_music.dependencies.database import get_session
from cue_the_music.integrations.discogs_client import (
    DiscogsArtist,
    DiscogsBasicInformation,
    DiscogsCollectionRelease,
    DiscogsCollectionResponse,
    DiscogsLabel,
    DiscogsPagination,
    get_discogs_client,
)
from cue_the_music.main import create_app


def _make_settings() -> Settings:
    """Create test settings."""
    return Settings(
        DISCOGS_TOKEN="test-token",
        DISCOGS_USERNAME="testuser",
        HOST_PIN="1234",
    )


def _make_collection_response() -> DiscogsCollectionResponse:
    """Build a one-page collection response with a single release."""
    return DiscogsCollectionResponse(
        pagination=DiscogsPagination(page=1, pages=1, per_page=100),
        releases=[
            DiscogsCollectionRelease(
                basic_information=DiscogsBasicInformation(
                    artists=[DiscogsArtist(name="Miles Davis")],
                    cover_image="https://img.discogs.com/full.jpg",
                    genres=["Jazz"],
                    id=12345,
                    labels=[DiscogsLabel(name="Columbia")],
                    styles=["Modal"],
                    thumb="https://img.discogs.com/thumb.jpg",
                    title="Kind of Blue",
                    year=1959,
                )
            )
        ],
    )


@pytest.mark.asyncio
class TestSyncEndpoint:
    """Tests for POST /api/host/sync."""

    async def test_sync_returns_result(self, async_engine) -> None:
        """A successful sync returns status and album count."""
        app = create_app()

        session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )

        async def override_get_session():
            async with session_factory() as session, session.begin():
                yield session

        mock_client = AsyncMock()
        mock_client.get_collection_page.return_value = (
            _make_collection_response()
        )

        # Override all dependencies before making the request
        app.dependency_overrides[get_session] = override_get_session
        app.dependency_overrides[get_settings] = lambda: _make_settings()
        app.dependency_overrides[get_discogs_client] = lambda: mock_client

        # Patch the session factory used by SyncService._upsert_page
        with patch(
            "cue_the_music.services.sync_service.async_session_factory",
            session_factory,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as ac:
                response = await ac.post("/api/host/sync")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"
        assert data["albums_synced"] == 1

    async def test_sync_failure_returns_502(self, async_engine) -> None:
        """A Discogs API failure returns 502."""
        app = create_app()

        session_factory = async_sessionmaker(
            async_engine, expire_on_commit=False
        )

        async def override_get_session():
            async with session_factory() as session, session.begin():
                yield session

        mock_client = AsyncMock()
        mock_client.get_collection_page.side_effect = RuntimeError(
            "Network error"
        )

        # Override all dependencies before making the request
        app.dependency_overrides[get_session] = override_get_session
        app.dependency_overrides[get_settings] = lambda: _make_settings()
        app.dependency_overrides[get_discogs_client] = lambda: mock_client

        with patch(
            "cue_the_music.services.sync_service.async_session_factory",
            session_factory,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as ac:
                response = await ac.post("/api/host/sync")

        assert response.status_code == 502
        data = response.json()
        assert "sync" in data["detail"].lower() or "discogs" in data["detail"].lower()
