"""Async HTTP client for Reclaim.ai API."""

from typing import Any

import httpx

from reclaim_mcp.config import Settings


class ReclaimClient:
    """Async client for interacting with the Reclaim.ai API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the client with settings."""
        self.base_url = settings.base_url
        self.headers = {
            "Authorization": f"Bearer {settings.api_key}",
            "Content-Type": "application/json",
        }

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request to the API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def post(self, endpoint: str, data: dict[str, Any]) -> Any:
        """Make a POST request to the API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def patch(self, endpoint: str, data: dict[str, Any]) -> Any:
        """Make a PATCH request to the API."""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def delete(self, endpoint: str) -> bool:
        """Make a DELETE request to the API."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
            )
            return response.status_code in (200, 204)
