"""Async HTTP client for Reclaim.ai API."""

import json
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

    def _parse_error_message(self, response: httpx.Response) -> str:
        """Parse error message from API response.

        Attempts to extract a meaningful error message from JSON responses,
        falling back to truncated text for non-JSON responses.

        Args:
            response: The httpx response object

        Returns:
            A user-friendly error message string
        """
        if not response.text:
            return "No details provided"

        try:
            error_data = json.loads(response.text)
            # Common error response formats
            if isinstance(error_data, dict):
                # Check for common error message fields
                for key in ("message", "error", "detail", "errorMessage", "msg"):
                    if key in error_data:
                        msg = error_data[key]
                        if isinstance(msg, str):
                            return msg
                        elif isinstance(msg, dict) and "message" in msg:
                            return msg["message"]
                # Check for nested errors array
                if "errors" in error_data and isinstance(error_data["errors"], list):
                    error_msgs = []
                    for err in error_data["errors"][:3]:  # Limit to first 3 errors
                        if isinstance(err, str):
                            error_msgs.append(err)
                        elif isinstance(err, dict):
                            err_msg = err.get("message") or err.get("msg") or str(err)
                            error_msgs.append(str(err_msg))
                    if error_msgs:
                        return "; ".join(error_msgs)
            # If we couldn't extract a message, return truncated JSON
            return response.text[:200]
        except json.JSONDecodeError:
            # Not JSON, return truncated text
            return response.text[:200]

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
        if response.status_code == 403:
            detail = self._parse_error_message(response)
            raise APIError(f"Access denied (403): {detail}. This may be a plan/tier restriction.")
        if response.status_code >= 500:
            detail = self._parse_error_message(response)
            raise APIError(f"Reclaim API server error ({response.status_code}): {detail}")
        if response.status_code >= 400:
            detail = self._parse_error_message(response)
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

    async def put(
        self,
        endpoint: str,
        data: dict[str, Any],
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make a PUT request to the API."""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data,
                params=params,
            )
            self._handle_response_errors(response, endpoint)
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
