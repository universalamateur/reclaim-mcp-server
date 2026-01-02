"""Async HTTP client for Reclaim.ai API."""

from typing import Any

import httpx

from reclaim_mcp.config import Settings
from reclaim_mcp.exceptions import APIError, NotFoundError, RateLimitError


class ReclaimClient:
    """Async client for interacting with the Reclaim.ai API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the client with settings."""
        self.base_url = settings.base_url
        self.headers = {
            "Authorization": f"Bearer {settings.api_key}",
            "Content-Type": "application/json",
        }

    def _handle_response_errors(self, response: httpx.Response, endpoint: str) -> None:
        """Check response for errors and raise appropriate exceptions.

        Args:
            response: The httpx response object
            endpoint: The API endpoint (for error messages)

        Raises:
            RateLimitError: If rate limit exceeded (429)
            NotFoundError: If resource not found (404)
            APIError: For other 4xx/5xx errors
        """
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            raise RateLimitError(f"Rate limit exceeded. Wait {retry_after}s before retrying.")
        if response.status_code == 404:
            raise NotFoundError(f"Resource not found: {endpoint}")
        if response.status_code == 401:
            raise APIError("Authentication failed. Please check your RECLAIM_API_KEY.")
        if response.status_code >= 400:
            # Truncate response text to avoid overwhelming error messages
            detail = response.text[:200] if response.text else "No details"
            raise APIError(f"API error {response.status_code}: {detail}")

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request to the API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
            )
            self._handle_response_errors(response, endpoint)
            return response.json()

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any],
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make a POST request to the API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data,
                params=params,
            )
            self._handle_response_errors(response, endpoint)
            # Handle empty response bodies (some endpoints return no content)
            if not response.content:
                return {}
            return response.json()

    async def patch(self, endpoint: str, data: dict[str, Any]) -> Any:
        """Make a PATCH request to the API."""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data,
            )
            self._handle_response_errors(response, endpoint)
            return response.json()

    async def delete(self, endpoint: str) -> bool:
        """Make a DELETE request to the API.

        Note: DELETE returns bool for backwards compatibility.
        Errors are raised as exceptions.
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
            )
            # For DELETE, 404 might be acceptable (resource already gone)
            if response.status_code == 404:
                return False
            self._handle_response_errors(response, endpoint)
            return response.status_code in (200, 204)
