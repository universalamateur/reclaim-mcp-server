"""Analytics tools for Reclaim.ai."""

from typing import Any

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from reclaim_mcp.cache import ttl_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import RateLimitError, ReclaimError
from reclaim_mcp.models import DateRange, UserAnalyticsRequest


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


def _format_validation_errors(e: ValidationError) -> str:
    """Format Pydantic validation errors into a user-friendly message."""
    errors = "; ".join(err["msg"] for err in e.errors())
    return f"Invalid input: {errors}"


@ttl_cache(ttl=300)
async def get_user_analytics(
    start: str,
    end: str,
    metric_name: str,
) -> dict:
    """Get personal productivity analytics for the current user.

    Args:
        start: Start date in ISO format (e.g., '2026-01-01')
        end: End date in ISO format (e.g., '2026-01-31')
        metric_name: The metric to retrieve. One of:
            - DURATION_BY_CATEGORY
            - DURATION_BY_DATE_BY_CATEGORY
            - HOURS_DEFENDED
            - FOCUS_WORK_BALANCE

    Returns:
        Analytics data with time breakdowns by category.
    """
    # Validate input using Pydantic model
    try:
        validated = UserAnalyticsRequest(
            start=start,
            end=end,
            metric_name=metric_name,  # type: ignore[arg-type]
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        params: dict[str, Any] = {
            "start": validated.start,
            "end": validated.end,
            "metricName": validated.metric_name.value,
        }

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
    # Validate input using Pydantic model
    try:
        validated = DateRange(start=start, end=end)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        params: dict[str, Any] = {
            "start": validated.start,
            "end": validated.end,
        }

        result = await client.get("/api/analytics/focus/insights/V3", params=params)
        return result
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting focus insights: {e}")
