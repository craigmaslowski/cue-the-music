"""Tests for queue, vote, and host queue API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from cue_the_music.models.album import Album
from tests.conftest import get_host_token


async def _seed_album(async_engine, **overrides) -> dict:
    """Insert an album directly via session for endpoint testing."""
    defaults = {
        "artist": "Test Artist",
        "cover_art_thumbnail_url": "https://example.com/thumb.jpg",
        "cover_art_url": "https://example.com/cover.jpg",
        "discogs_release_id": "e001",
        "genre_tags": ["Rock"],
        "label": "Test Label",
        "style_tags": ["Punk"],
        "title": "Test Album",
        "year": 1977,
    }
    defaults.update(overrides)
    session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
    async with session_factory() as session, session.begin():
        album = Album(**defaults)
        session.add(album)
        await session.flush()
        album_id = album.id
    return {**defaults, "id": album_id}


@pytest.mark.asyncio
class TestQueueEndpoints:
    """Tests for GET/POST/DELETE /api/queue."""

    async def test_get_empty_queue(self, client: AsyncClient) -> None:
        response = await client.get("/api/queue")

        assert response.status_code == 200
        data = response.json()
        assert data["now_playing"] is None
        assert data["queue"] == []
        assert data["count"] == 0

    async def test_add_to_queue(
        self, client: AsyncClient, async_engine
    ) -> None:
        album = await _seed_album(async_engine, discogs_release_id="e002")

        response = await client.post(
            "/api/queue", json={"album_id": album["id"]}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["album"]["id"] == album["id"]
        assert data["votes"]["up_count"] == 1
        assert data["votes"]["my_vote"] == 1
        assert data["votes"]["down_count"] == 0

    async def test_add_duplicate_album_returns_409(
        self, client: AsyncClient, async_engine
    ) -> None:
        album = await _seed_album(async_engine, discogs_release_id="e003")

        await client.post("/api/queue", json={"album_id": album["id"]})
        response = await client.post(
            "/api/queue", json={"album_id": album["id"]}
        )

        assert response.status_code == 409

    async def test_add_nonexistent_album_returns_404(
        self, client: AsyncClient
    ) -> None:
        response = await client.post("/api/queue", json={"album_id": 9999})

        assert response.status_code == 404

    async def test_cancel_own_request(
        self, client: AsyncClient, async_engine
    ) -> None:
        album = await _seed_album(async_engine, discogs_release_id="e004")
        add_response = await client.post(
            "/api/queue", json={"album_id": album["id"]}
        )
        queue_item_id = add_response.json()["id"]

        response = await client.delete(f"/api/queue/{queue_item_id}")

        assert response.status_code == 204

    async def test_queue_state_includes_items(
        self, client: AsyncClient, async_engine
    ) -> None:
        album = await _seed_album(async_engine, discogs_release_id="e005")
        await client.post("/api/queue", json={"album_id": album["id"]})

        response = await client.get("/api/queue")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["queue"][0]["album"]["artist"] == "Test Artist"

    async def test_request_limit_enforced(
        self, client: AsyncClient, async_engine
    ) -> None:
        albums = []
        for i in range(4):
            a = await _seed_album(
                async_engine, discogs_release_id=f"e010{i}"
            )
            albums.append(a)

        # First 3 should succeed
        for i in range(3):
            resp = await client.post(
                "/api/queue", json={"album_id": albums[i]["id"]}
            )
            assert resp.status_code == 201

        # Fourth should be rejected
        resp = await client.post(
            "/api/queue", json={"album_id": albums[3]["id"]}
        )
        assert resp.status_code == 429


@pytest.mark.asyncio
class TestVoteEndpoints:
    """Tests for PUT/DELETE /api/queue/{id}/vote."""

    async def test_cast_vote(
        self, client: AsyncClient, async_engine
    ) -> None:
        album = await _seed_album(async_engine, discogs_release_id="e020")
        add_resp = await client.post(
            "/api/queue", json={"album_id": album["id"]}
        )
        qi_id = add_resp.json()["id"]

        response = await client.put(
            f"/api/queue/{qi_id}/vote", json={"value": 1}
        )

        assert response.status_code == 204

    async def test_vote_on_nonexistent_returns_404(
        self, client: AsyncClient
    ) -> None:
        response = await client.put(
            "/api/queue/9999/vote", json={"value": 1}
        )

        assert response.status_code == 404

    async def test_remove_vote(
        self, client: AsyncClient, async_engine
    ) -> None:
        album = await _seed_album(async_engine, discogs_release_id="e021")
        add_resp = await client.post(
            "/api/queue", json={"album_id": album["id"]}
        )
        qi_id = add_resp.json()["id"]

        # Cast then remove
        await client.put(f"/api/queue/{qi_id}/vote", json={"value": 1})
        response = await client.delete(f"/api/queue/{qi_id}/vote")

        assert response.status_code == 204

    async def test_vote_reflected_in_queue_state(
        self, client: AsyncClient, async_engine
    ) -> None:
        album = await _seed_album(async_engine, discogs_release_id="e022")
        add_resp = await client.post(
            "/api/queue", json={"album_id": album["id"]}
        )
        qi_id = add_resp.json()["id"]

        await client.put(f"/api/queue/{qi_id}/vote", json={"value": 1})

        response = await client.get("/api/queue")
        data = response.json()
        item = data["queue"][0]
        assert item["votes"]["up_count"] == 1
        assert item["votes"]["my_vote"] == 1


@pytest.mark.asyncio
class TestHostQueueEndpoints:
    """Tests for host queue management endpoints."""

    async def test_promote_to_now_playing(
        self, client: AsyncClient, async_engine, monkeypatch
    ) -> None:
        monkeypatch.setenv("HOST_PIN", "1234")
        token = await get_host_token(client)
        headers = {"X-Host-Token": token}

        album = await _seed_album(async_engine, discogs_release_id="e030")
        add_resp = await client.post(
            "/api/queue", json={"album_id": album["id"]}
        )
        qi_id = add_resp.json()["id"]

        response = await client.post(
            "/api/host/now-playing",
            json={"queue_item_id": qi_id},
            headers=headers,
        )

        assert response.status_code == 204

        # Queue should be empty, now playing should be set
        state = await client.get("/api/queue")
        data = state.json()
        assert data["count"] == 0
        assert data["now_playing"] is not None
        assert data["now_playing"]["album"]["id"] == album["id"]

    async def test_clear_now_playing(
        self, client: AsyncClient, async_engine, monkeypatch
    ) -> None:
        monkeypatch.setenv("HOST_PIN", "1234")
        token = await get_host_token(client)
        headers = {"X-Host-Token": token}

        album = await _seed_album(async_engine, discogs_release_id="e031")
        add_resp = await client.post(
            "/api/queue", json={"album_id": album["id"]}
        )
        qi_id = add_resp.json()["id"]

        await client.post(
            "/api/host/now-playing",
            json={"queue_item_id": qi_id},
            headers=headers,
        )

        response = await client.delete(
            "/api/host/now-playing", headers=headers
        )

        assert response.status_code == 204

        state = await client.get("/api/queue")
        assert state.json()["now_playing"] is None

    async def test_host_skip_queue_item(
        self, client: AsyncClient, async_engine, monkeypatch
    ) -> None:
        monkeypatch.setenv("HOST_PIN", "1234")
        token = await get_host_token(client)
        headers = {"X-Host-Token": token}

        album = await _seed_album(async_engine, discogs_release_id="e032")
        add_resp = await client.post(
            "/api/queue", json={"album_id": album["id"]}
        )
        qi_id = add_resp.json()["id"]

        response = await client.delete(
            f"/api/host/queue/{qi_id}", headers=headers
        )

        assert response.status_code == 204

        state = await client.get("/api/queue")
        assert state.json()["count"] == 0

    async def test_promote_nonexistent_returns_404(
        self, client: AsyncClient, monkeypatch
    ) -> None:
        monkeypatch.setenv("HOST_PIN", "1234")
        token = await get_host_token(client)
        headers = {"X-Host-Token": token}

        response = await client.post(
            "/api/host/now-playing",
            json={"queue_item_id": 9999},
            headers=headers,
        )

        assert response.status_code == 404

    async def test_clear_queue_removes_all_items_and_now_playing(
        self, client: AsyncClient, async_engine, monkeypatch
    ) -> None:
        monkeypatch.setenv("HOST_PIN", "1234")
        token = await get_host_token(client)
        headers = {"X-Host-Token": token}

        # Seed two albums, add both to queue, promote one to now playing
        album1 = await _seed_album(async_engine, discogs_release_id="e040")
        album2 = await _seed_album(async_engine, discogs_release_id="e041")
        resp1 = await client.post("/api/queue", json={"album_id": album1["id"]})
        await client.post("/api/queue", json={"album_id": album2["id"]})
        qi_id = resp1.json()["id"]
        await client.post(
            "/api/host/now-playing",
            json={"queue_item_id": qi_id},
            headers=headers,
        )

        response = await client.delete("/api/host/queue", headers=headers)

        assert response.status_code == 204

        state = await client.get("/api/queue")
        data = state.json()
        assert data["count"] == 0
        assert data["now_playing"] is None

    async def test_clear_queue_on_empty_is_idempotent(
        self, client: AsyncClient, monkeypatch
    ) -> None:
        monkeypatch.setenv("HOST_PIN", "1234")
        token = await get_host_token(client)
        headers = {"X-Host-Token": token}

        response = await client.delete("/api/host/queue", headers=headers)

        assert response.status_code == 204

    async def test_host_endpoints_reject_without_token(
        self, client: AsyncClient
    ) -> None:
        """Host endpoints require X-Host-Token header."""
        response = await client.post(
            "/api/host/now-playing", json={"queue_item_id": 1}
        )
        assert response.status_code == 403

        response = await client.delete("/api/host/now-playing")
        assert response.status_code == 403

        response = await client.delete("/api/host/queue")
        assert response.status_code == 403

        response = await client.delete("/api/host/queue/1")
        assert response.status_code == 403
