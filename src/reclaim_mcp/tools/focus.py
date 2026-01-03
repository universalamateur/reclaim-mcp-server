"""Focus time management tools for Reclaim.ai."""

from typing import Any, Optional

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from reclaim_mcp.cache import invalidate_cache, ttl_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import NotFoundError, RateLimitError, ReclaimError
from reclaim_mcp.models import CalendarEventId, FocusReschedule, FocusSettingsUpdate


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


def _format_validation_errors(e: ValidationError) -> str:
    """Format Pydantic validation errors into a user-friendly message."""
    errors = "; ".join(err["msg"] for err in e.errors())
    return f"Invalid input: {errors}"


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
    # Validate input using Pydantic model
    try:
        validated = FocusSettingsUpdate(
            min_duration_mins=min_duration_mins,
            ideal_duration_mins=ideal_duration_mins,
            max_duration_mins=max_duration_mins,
            defense_aggression=defense_aggression,  # type: ignore[arg-type]
            enabled=enabled,
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()

        update_data: dict[str, Any] = {}
        if validated.min_duration_mins is not None:
            update_data["minDurationMins"] = validated.min_duration_mins
        if validated.ideal_duration_mins is not None:
            update_data["idealDurationMins"] = validated.ideal_duration_mins
        if validated.max_duration_mins is not None:
            update_data["maxDurationMins"] = validated.max_duration_mins
        if validated.defense_aggression is not None:
            update_data["defenseAggression"] = validated.defense_aggression.value
        if validated.enabled is not None:
            update_data["enabled"] = validated.enabled

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
    # Validate input using Pydantic model
    try:
        validated = CalendarEventId(calendar_id=calendar_id, event_id=event_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(
            f"/api/focus/planner/{validated.calendar_id}/{validated.event_id}/lock",
            {},
        )
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(
            f"Focus block {validated.event_id} not found in calendar "
            f"{validated.calendar_id}"
        )
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error locking focus block {validated.event_id}: {e}")


async def unlock_focus_block(calendar_id: int, event_id: str) -> dict:
    """Unlock a focus time block to allow it to be rescheduled.

    Args:
        calendar_id: The calendar ID containing the focus block
        event_id: The focus block event ID to unlock

    Returns:
        Planner action result with updated event state.
    """
    # Validate input using Pydantic model
    try:
        validated = CalendarEventId(calendar_id=calendar_id, event_id=event_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(
            f"/api/focus/planner/{validated.calendar_id}/{validated.event_id}/unlock",
            {},
        )
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(
            f"Focus block {validated.event_id} not found in calendar "
            f"{validated.calendar_id}"
        )
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error unlocking focus block {validated.event_id}: {e}")


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
    # Validate input using Pydantic model
    try:
        validated = FocusReschedule(
            calendar_id=calendar_id,
            event_id=event_id,
            start_time=start_time,
            end_time=end_time,
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        payload: dict[str, Any] = {}
        if validated.start_time is not None:
            payload["start"] = validated.start_time
        if validated.end_time is not None:
            payload["end"] = validated.end_time

        result = await client.post(
            f"/api/focus/planner/{validated.calendar_id}/{validated.event_id}/reschedule",
            payload,
        )
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(
            f"Focus block {validated.event_id} not found in calendar "
            f"{validated.calendar_id}"
        )
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error rescheduling focus block {validated.event_id}: {e}")
