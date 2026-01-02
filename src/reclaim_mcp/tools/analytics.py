"""Analytics tools for Reclaim.ai."""

from typing import Any, Optional

from fastmcp.exceptions import ToolError

from reclaim_mcp.cache import ttl_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import RateLimitError, ReclaimError


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


@ttl_cache(ttl=300)
async def get_user_analytics(
    start: str,
    end: str,
    metric_names: Optional[list[str]] = None,
) -> dict:
    """Get personal productivity analytics for the current user.

    Args:
        start: Start date in ISO format (e.g., '2026-01-01')
        end: End date in ISO format (e.g., '2026-01-31')
        metric_names: Optional list of metrics to retrieve
            (DURATION_BY_CATEGORY, DURATION_BY_DATE_BY_CATEGORY, etc.)

    Returns:
        Analytics data with time breakdowns by category.
    """
    try:
        client = _get_client()
        params: dict[str, Any] = {
            "start": start,
            "end": end,
        }
        if metric_names:
            params["metricName"] = metric_names

        result = await client.get("/api/analytics/user/V3", params=params)
        return result
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting user analytics: {e}")


@ttl_cache(ttl=300)
async def get_focus_insights(
    start: str,
    end: str,
) -> dict:
    """Get focus time insights and recommendations.

    Args:
        start: Start date in ISO format (e.g., '2026-01-01')
        end: End date in ISO format (e.g., '2026-01-31')

    Returns:
        Focus time analytics including protected hours, interruptions, etc.
    """
    try:
        client = _get_client()
        params: dict[str, Any] = {
            "start": start,
            "end": end,
        }

        result = await client.get("/api/analytics/focus/insights/V3", params=params)
        return result
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting focus insights: {e}")
