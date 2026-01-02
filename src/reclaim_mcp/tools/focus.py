"""Focus time management tools for Reclaim.ai."""

from typing import Any, Optional

from fastmcp.exceptions import ToolError

from reclaim_mcp.cache import invalidate_cache, ttl_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import NotFoundError, RateLimitError, ReclaimError


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


@ttl_cache(ttl=120)
async def get_focus_settings() -> list[dict]:
    """Get current focus time settings for the user.

    Returns:
        List of focus settings objects (one per focus type).
    """
    try:
        client = _get_client()
        result = await client.get("/api/focus-settings/user")
        return result
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting focus settings: {e}")


async def update_focus_settings(
    settings_id: int,
    min_duration_mins: Optional[int] = None,
    ideal_duration_mins: Optional[int] = None,
    max_duration_mins: Optional[int] = None,
    defense_aggression: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> dict:
    """Update focus time settings.

    Args:
        settings_id: The focus settings ID to update
        min_duration_mins: Minimum focus block duration in minutes
        ideal_duration_mins: Ideal focus block duration in minutes
        max_duration_mins: Maximum focus block duration in minutes
        defense_aggression: Protection level (NONE, LOW, MEDIUM, HIGH, MAX)
        enabled: Whether focus time is enabled

    Returns:
        Updated focus settings.
    """
    try:
        client = _get_client()

        update_data: dict[str, Any] = {}
        if min_duration_mins is not None:
            update_data["minDurationMins"] = min_duration_mins
        if ideal_duration_mins is not None:
            update_data["idealDurationMins"] = ideal_duration_mins
        if max_duration_mins is not None:
            update_data["maxDurationMins"] = max_duration_mins
        if defense_aggression is not None:
            update_data["defenseAggression"] = defense_aggression
        if enabled is not None:
            update_data["enabled"] = enabled

        result = await client.patch(f"/api/focus-settings/user/{settings_id}", update_data)
        invalidate_cache("get_focus_settings")
        return result
    except NotFoundError:
        raise ToolError(f"Focus settings {settings_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error updating focus settings: {e}")


async def lock_focus_block(calendar_id: int, event_id: str) -> dict:
    """Lock a focus time block to prevent it from being rescheduled.

    Args:
        calendar_id: The calendar ID containing the focus block
        event_id: The focus block event ID to lock

    Returns:
        Planner action result with updated event state.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/focus/planner/{calendar_id}/{event_id}/lock", {})
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(f"Focus block {event_id} not found in calendar {calendar_id}")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error locking focus block {event_id}: {e}")


async def unlock_focus_block(calendar_id: int, event_id: str) -> dict:
    """Unlock a focus time block to allow it to be rescheduled.

    Args:
        calendar_id: The calendar ID containing the focus block
        event_id: The focus block event ID to unlock

    Returns:
        Planner action result with updated event state.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/focus/planner/{calendar_id}/{event_id}/unlock", {})
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(f"Focus block {event_id} not found in calendar {calendar_id}")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error unlocking focus block {event_id}: {e}")


async def reschedule_focus_block(
    calendar_id: int,
    event_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> dict:
    """Reschedule a focus time block to a different time.

    Args:
        calendar_id: The calendar ID containing the focus block
        event_id: The focus block event ID to reschedule
        start_time: New start time in ISO format (optional, triggers AI reschedule if not provided)
        end_time: New end time in ISO format (optional)

    Returns:
        Planner action result with updated event state.
    """
    try:
        client = _get_client()
        payload: dict[str, Any] = {}
        if start_time is not None:
            payload["start"] = start_time
        if end_time is not None:
            payload["end"] = end_time

        result = await client.post(
            f"/api/focus/planner/{calendar_id}/{event_id}/reschedule",
            payload,
        )
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(f"Focus block {event_id} not found in calendar {calendar_id}")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error rescheduling focus block {event_id}: {e}")
