"""Tests for DiscogsClient with mocked httpx responses."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from cue_the_music.config import Settings
from cue_the_music.integrations.discogs_client import DiscogsClient

_HTTPX_CLIENT_PATH = (
    "cue_the_music.integrations.discogs_client.httpx.AsyncClient"
)


def _make_settings() -> Settings:
    """Create test settings with dummy Discogs credentials."""
    return Settings(
        DISCOGS_TOKEN="test-token-abc123",
        DISCOGS_USERNAME="testuser",
        HOST_PIN="1234",
    )


def _make_collection_response_json(
    page: int = 1, pages: int = 1
) -> dict:
    """Build a minimal Discogs collection API response."""
    return {
        "pagination": {
            "page": page,
            "pages": pages,
            "per_page": 100,
        },
        "releases": [
            {
                "basic_information": {
                    "artists": [{"name": "Miles Davis"}],
                    "cover_image": "https://img.discogs.com/full.jpg",
                    "genres": ["Jazz"],
                    "id": 12345,
                    "labels": [{"name": "Columbia"}],
                    "styles": ["Modal"],
                    "thumb": "https://img.discogs.com/thumb.jpg",
                    "title": "Kind of Blue",
                    "year": 1959,
                }
            }
        ],
    }


def _make_release_detail_json() -> dict:
    """Build a minimal Discogs release detail API response."""
    return {
        "id": 12345,
        "tracklist": [
            {
                "duration": "9:22",
                "position": "A1",
                "title": "So What",
                "type_": "track",
            },
            {
                "duration": "9:46",
                "position": "A2",
                "title": "Freddie Freeloader",
                "type_": "track",
            },
        ],
    }


@pytest.mark.asyncio
class TestDiscogsClientGetCollectionPage:
    """Tests for DiscogsClient.get_collection_page()."""

    async def test_fetches_and_validates_collection_page(self) -> None:
        client = DiscogsClient(_make_settings())
        mock_response = httpx.Response(
            200,
            json=_make_collection_response_json(),
            request=httpx.Request("GET", "https://api.discogs.com/test"),
        )

        with patch(_HTTPX_CLIENT_PATH) as mock_cls:
            mock_http = AsyncMock()
            mock_http.get.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            result = await client.get_collection_page("testuser", page=1)

        assert result.pagination.page == 1
        assert result.pagination.pages == 1
        assert len(result.releases) == 1
        assert result.releases[0].basic_information.title == "Kind of Blue"
        assert result.releases[0].basic_information.artists[0].name == "Miles Davis"

    async def test_sends_auth_header_and_user_agent(self) -> None:
        client = DiscogsClient(_make_settings())
        mock_response = httpx.Response(
            200,
            json=_make_collection_response_json(),
            request=httpx.Request("GET", "https://api.discogs.com/test"),
        )

        with patch(_HTTPX_CLIENT_PATH) as mock_cls:
            mock_http = AsyncMock()
            mock_http.get.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            await client.get_collection_page("testuser", page=1)

        # Verify headers include auth token and custom user agent
        call_kwargs = mock_http.get.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert headers["Authorization"] == "Discogs token=test-token-abc123"
        assert headers["User-Agent"] == "CueTheMusic/1.0"

    async def test_raises_on_http_error(self) -> None:
        client = DiscogsClient(_make_settings())
        mock_response = httpx.Response(
            429,
            json={"message": "Rate limit exceeded"},
            request=httpx.Request("GET", "https://api.discogs.com/test"),
        )

        with patch(_HTTPX_CLIENT_PATH) as mock_cls:
            mock_http = AsyncMock()
            mock_http.get.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            with pytest.raises(httpx.HTTPStatusError):
                await client.get_collection_page("testuser", page=1)

    async def test_multi_page_pagination(self) -> None:
        client = DiscogsClient(_make_settings())
        mock_response = httpx.Response(
            200,
            json=_make_collection_response_json(page=2, pages=5),
            request=httpx.Request("GET", "https://api.discogs.com/test"),
        )

        with patch(_HTTPX_CLIENT_PATH) as mock_cls:
            mock_http = AsyncMock()
            mock_http.get.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            result = await client.get_collection_page("testuser", page=2)

        assert result.pagination.page == 2
        assert result.pagination.pages == 5


@pytest.mark.asyncio
class TestDiscogsClientGetReleaseDetail:
    """Tests for DiscogsClient.get_release_detail()."""

    async def test_fetches_and_validates_release_detail(self) -> None:
        client = DiscogsClient(_make_settings())
        mock_response = httpx.Response(
            200,
            json=_make_release_detail_json(),
            request=httpx.Request("GET", "https://api.discogs.com/test"),
        )

        with patch(_HTTPX_CLIENT_PATH) as mock_cls:
            mock_http = AsyncMock()
            mock_http.get.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            result = await client.get_release_detail(12345)

        assert result.id == 12345
        assert len(result.tracklist) == 2
        assert result.tracklist[0].title == "So What"
        assert result.tracklist[0].position == "A1"
        assert result.tracklist[0].duration == "9:22"

    async def test_raises_on_http_error(self) -> None:
        client = DiscogsClient(_make_settings())
        mock_response = httpx.Response(
            404,
            json={"message": "Release not found"},
            request=httpx.Request("GET", "https://api.discogs.com/test"),
        )

        with patch(_HTTPX_CLIENT_PATH) as mock_cls:
            mock_http = AsyncMock()
            mock_http.get.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = mock_http

            with pytest.raises(httpx.HTTPStatusError):
                await client.get_release_detail(99999)
