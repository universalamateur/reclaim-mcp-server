"""Tests for the Reclaim.ai API client."""

import pytest
from httpx import Request, Response
from pytest import MonkeyPatch

from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import Settings


def _make_response(status_code: int, json_data: dict | list | None = None) -> Response:
    """Create a Response with a dummy request for raise_for_status() to work."""
    request = Request("GET", "https://test.example.com")
    return Response(status_code, json=json_data, request=request)


class TestReclaimClient:
    """Tests for ReclaimClient."""

    def test_client_initialization(self, settings: Settings) -> None:
        """Test client is initialized with correct headers."""
        client = ReclaimClient(settings)

        assert client.base_url == "https://api.app.reclaim.ai"
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test_api_key_12345"
        assert client.headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_request(
        self, settings: Settings, mock_tasks_list_response: list[dict], monkeypatch: MonkeyPatch
    ) -> None:
        """Test GET request returns parsed JSON."""

        async def mock_get(*args, **kwargs):
            return _make_response(200, mock_tasks_list_response)

        monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

        client = ReclaimClient(settings)
        result = await client.get("/api/tasks")

        assert result == mock_tasks_list_response
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_post_request(self, settings: Settings, mock_task_response: dict, monkeypatch: MonkeyPatch) -> None:
        """Test POST request returns parsed JSON."""

        async def mock_post(*args, **kwargs):
            return _make_response(201, mock_task_response)

        monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

        client = ReclaimClient(settings)
        result = await client.post("/api/tasks", {"title": "Test Task", "timeChunksRequired": 4})

        assert result["id"] == 12345
        assert result["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_delete_request_success(self, settings: Settings, monkeypatch: MonkeyPatch) -> None:
        """Test DELETE request returns True on success."""

        async def mock_delete(*args, **kwargs):
            return _make_response(204)

        monkeypatch.setattr("httpx.AsyncClient.delete", mock_delete)

        client = ReclaimClient(settings)
        result = await client.delete("/api/tasks/12345")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_request_not_found(self, settings: Settings, monkeypatch: MonkeyPatch) -> None:
        """Test DELETE request returns False on 404."""

        async def mock_delete(*args, **kwargs):
            return _make_response(404)

        monkeypatch.setattr("httpx.AsyncClient.delete", mock_delete)

        client = ReclaimClient(settings)
        result = await client.delete("/api/tasks/99999")

        assert result is False

    @pytest.mark.asyncio
    async def test_get_request_rate_limit(self, settings: Settings, monkeypatch: MonkeyPatch) -> None:
        """Test GET request raises RateLimitError on 429."""
        from reclaim_mcp.exceptions import RateLimitError

        async def mock_get(*args, **kwargs):
            request = Request("GET", "https://test.example.com")
            return Response(429, headers={"Retry-After": "30"}, request=request)

        monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

        client = ReclaimClient(settings)
        with pytest.raises(RateLimitError) as exc_info:
            await client.get("/api/tasks")

        assert "30s" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_request_not_found(self, settings: Settings, monkeypatch: MonkeyPatch) -> None:
        """Test GET request raises NotFoundError on 404."""
        from reclaim_mcp.exceptions import NotFoundError

        async def mock_get(*args, **kwargs):
            request = Request("GET", "https://test.example.com")
            return Response(404, request=request)

        monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

        client = ReclaimClient(settings)
        with pytest.raises(NotFoundError):
            await client.get("/api/tasks/99999")

    @pytest.mark.asyncio
    async def test_get_request_auth_error(self, settings: Settings, monkeypatch: MonkeyPatch) -> None:
        """Test GET request raises APIError on 401."""
        from reclaim_mcp.exceptions import APIError

        async def mock_get(*args, **kwargs):
            request = Request("GET", "https://test.example.com")
            return Response(401, request=request)

        monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

        client = ReclaimClient(settings)
        with pytest.raises(APIError) as exc_info:
            await client.get("/api/tasks")

        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_request_server_error(self, settings: Settings, monkeypatch: MonkeyPatch) -> None:
        """Test GET request raises APIError on 500."""
        from reclaim_mcp.exceptions import APIError

        async def mock_get(*args, **kwargs):
            request = Request("GET", "https://test.example.com")
            return Response(500, text="Internal Server Error", request=request)

        monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

        client = ReclaimClient(settings)
        with pytest.raises(APIError) as exc_info:
            await client.get("/api/tasks")

        assert "server error (500)" in str(exc_info.value)
