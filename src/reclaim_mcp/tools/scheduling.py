"""Scheduling tools — working hours and meeting time suggestions."""

from typing import Optional

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from reclaim_mcp.cache import ttl_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import RateLimitError, ReclaimError
from reclaim_mcp.models import SuggestedTimesRequest
from reclaim_mcp.utils import format_validation_errors


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


@ttl_cache(ttl=300)
async def get_working_hours() -> list:
    """Get all time schemes (working hours / availability windows).

    Returns:
        List of time scheme objects with schedule policies and day-by-day hours.
    """
    try:
        client = _get_client()
        result = await client.get("/api/timeschemes")
        return result
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting working hours: {e}")


async def find_available_times(
    attendees: list[str],
    duration_minutes: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """Find available meeting times for a set of attendees.

    Args:
        attendees: List of email addresses to find mutual availability for.
        duration_minutes: Required meeting duration in minutes.
        start_date: Start of search window in YYYY-MM-DD format (optional).
        end_date: End of search window in YYYY-MM-DD format (optional).
        limit: Maximum number of suggested times to return (optional).

    Returns:
        Suggested times with availability info for each slot.
    """
    try:
        validated = SuggestedTimesRequest(
            attendees=attendees,
            duration_minutes=duration_minutes,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
    except ValidationError as e:
        raise ToolError(format_validation_errors(e))

    payload: dict = {
        "attendees": validated.attendees,
        "durationMinutes": validated.duration_minutes,
    }
    if validated.start_date and validated.end_date:
        payload["scheduleWindow"] = {
            "start": validated.start_date,
            "end": validated.end_date,
        }
    if validated.limit is not None:
        payload["limit"] = validated.limit

    try:
        client = _get_client()
        return await client.post("/api/availability/suggested-times", data=payload)
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error finding available times: {e}")
