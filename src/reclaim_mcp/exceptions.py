"""Custom exceptions for Reclaim MCP server."""


class ReclaimError(Exception):
    """Base exception for Reclaim MCP errors."""

    pass


class NotFoundError(ReclaimError):
    """Resource not found (404)."""

    pass


class RateLimitError(ReclaimError):
    """Rate limit exceeded (429)."""

    pass


class APIError(ReclaimError):
    """General API error."""

    pass
