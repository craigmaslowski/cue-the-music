"""Tests for host PIN verification and host auth dependency."""

import pytest
from httpx import AsyncClient

from cue_the_music.services.host_auth_service import HostAuthService


@pytest.mark.asyncio
class TestPinVerificationEndpoint:
    """Tests for POST /api/host/verify-pin."""

    async def test_correct_pin_returns_token(
        self, client: AsyncClient, monkeypatch
    ) -> None:
        """Correct PIN returns a 200 with a session token."""
        monkeypatch.setenv("HOST_PIN", "1234")

        response = await client.post(
            "/api/host/verify-pin", json={"pin": "1234"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 0

    async def test_wrong_pin_returns_401(
        self, client: AsyncClient, monkeypatch
    ) -> None:
        """Wrong PIN returns 401 Unauthorized."""
        monkeypatch.setenv("HOST_PIN", "5678")

        response = await client.post(
            "/api/host/verify-pin", json={"pin": "0000"}
        )

        assert response.status_code == 401

    async def test_invalid_pin_format_returns_422(
        self, client: AsyncClient
    ) -> None:
        """Non-4-digit PIN returns 422 validation error."""
        response = await client.post(
            "/api/host/verify-pin", json={"pin": "abc"}
        )
        assert response.status_code == 422

        response = await client.post(
            "/api/host/verify-pin", json={"pin": "12345"}
        )
        assert response.status_code == 422

    async def test_rate_limiting_returns_429(
        self, client: AsyncClient, monkeypatch
    ) -> None:
        """Exceeding 5 attempts per minute returns 429."""
        monkeypatch.setenv("HOST_PIN", "9999")

        # Make 5 wrong attempts (each has a 500ms delay)
        for _ in range(5):
            await client.post(
                "/api/host/verify-pin", json={"pin": "0000"}
            )

        # 6th attempt should be rate-limited
        response = await client.post(
            "/api/host/verify-pin", json={"pin": "0000"}
        )

        assert response.status_code == 429


@pytest.mark.asyncio
class TestHostAuthDependency:
    """Tests for X-Host-Token header validation."""

    async def test_valid_token_passes(
        self, client: AsyncClient, monkeypatch
    ) -> None:
        """A valid host token allows access to host endpoints."""
        monkeypatch.setenv("HOST_PIN", "1234")

        # Get a valid token
        pin_resp = await client.post(
            "/api/host/verify-pin", json={"pin": "1234"}
        )
        token = pin_resp.json()["token"]

        # Delete now-playing should work (even if nothing is playing, 204 is fine)
        response = await client.delete(
            "/api/host/now-playing",
            headers={"X-Host-Token": token},
        )

        assert response.status_code == 204

    async def test_missing_token_returns_403(
        self, client: AsyncClient
    ) -> None:
        """Missing X-Host-Token header returns 403."""
        response = await client.delete("/api/host/now-playing")
        assert response.status_code == 403

    async def test_invalid_token_returns_403(
        self, client: AsyncClient
    ) -> None:
        """An invalid/bogus token returns 403."""
        response = await client.delete(
            "/api/host/now-playing",
            headers={"X-Host-Token": "totally-fake-token"},
        )
        assert response.status_code == 403

    async def test_expired_token_returns_403(self) -> None:
        """An expired token is rejected."""
        from datetime import UTC, datetime, timedelta

        from cue_the_music.services.host_auth_service import HostTokenInfo

        service = HostAuthService()

        # Manually set a token that expired 5 hours ago
        service._active_token = "test-token-123"
        service._token_info = HostTokenInfo(
            created_at=datetime.now(tz=UTC) - timedelta(hours=5),
            ip="127.0.0.1",
        )

        assert service.validate_token("test-token-123") is False
