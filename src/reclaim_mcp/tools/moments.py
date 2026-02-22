"""Moment/context tools for Reclaim.ai — what's happening now and next."""

from fastmcp.exceptions import ToolError

from reclaim_mcp.cache import ttl_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import RateLimitError, ReclaimError


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


@ttl_cache(ttl=15)
async def get_current_moment() -> dict:
    """Get what the user is currently doing right now.

    Returns:
        Current moment with active event, task, or free time info.
    """
    try:
        client = _get_client()
        result = await client.get("/api/moment")
        return result
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting current moment: {e}")


@ttl_cache(ttl=15)
async def get_next_moment() -> dict:
    """Get what's coming up next on the user's schedule.

    Returns:
        Next upcoming event, task, or transition info.
    """
    try:
        client = _get_client()
        result = await client.get("/api/moment/next")
        return result
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting next moment: {e}")
