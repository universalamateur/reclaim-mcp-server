"""Smart Habit tools for Reclaim.ai."""

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
async def list_habits() -> list[dict]:
    """List all smart habits from Reclaim.ai.

    Returns:
        List of habit objects with lineageId, title, enabled, recurrence, etc.
    """
    try:
        client = _get_client()
        habits = await client.get("/api/smart-habits")
        return habits
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error listing habits: {e}")


@ttl_cache(ttl=60)
async def get_habit(lineage_id: int) -> dict:
    """Get a single smart habit by lineage ID.

    Args:
        lineage_id: The habit lineage ID to retrieve

    Returns:
        SmartHabitLineageView object with full details.
    """
    try:
        client = _get_client()
        habit = await client.get(f"/api/smart-habits/{lineage_id}")
        return habit
    except NotFoundError:
        raise ToolError(f"Habit {lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting habit {lineage_id}: {e}")


async def create_habit(
    title: str,
    ideal_time: str,
    duration_min_mins: int,
    frequency: str = "WEEKLY",
    ideal_days: Optional[list[str]] = None,
    event_type: str = "SOLO_WORK",
    defense_aggression: str = "DEFAULT",
    duration_max_mins: Optional[int] = None,
    description: Optional[str] = None,
    enabled: bool = True,
    time_policy_type: Optional[str] = None,
) -> dict:
    """Create a new smart habit for auto-scheduling.

    Args:
        title: Habit name/title
        ideal_time: Preferred time in "HH:MM" format (e.g., "09:00")
        duration_min_mins: Minimum duration in minutes
        frequency: Recurrence (DAILY, WEEKLY, MONTHLY, YEARLY) - default WEEKLY
        ideal_days: Days for WEEKLY frequency (MONDAY, TUESDAY, etc.)
        event_type: Type (FOCUS, SOLO_WORK, PERSONAL, etc.) - default SOLO_WORK
        defense_aggression: Protection level (DEFAULT, NONE, LOW, MEDIUM, HIGH, MAX)
        duration_max_mins: Maximum duration in minutes (defaults to min duration)
        description: Optional habit description
        enabled: Whether habit is active (default True)
        time_policy_type: Time policy (WORK, PERSONAL, MEETING). Auto-inferred if not provided.

    Returns:
        Created habit object.
    """
    # Validate: ideal_days cannot be used with DAILY frequency
    if frequency == "DAILY" and ideal_days is not None:
        raise ToolError("'ideal_days' cannot be used with DAILY frequency. Use WEEKLY or MONTHLY.")

    try:
        client = _get_client()

        # Build recurrence object
        recurrence: dict[str, Any] = {"frequency": frequency}
        if ideal_days:
            recurrence["idealDays"] = ideal_days

        # Determine time policy type based on event type if not explicitly provided
        if time_policy_type is None:
            if event_type == "PERSONAL":
                time_policy_type = "PERSONAL"
            else:
                time_policy_type = "WORK"

        # Normalize ideal time to HH:MM:SS format
        if len(ideal_time) == 5:  # HH:MM format
            ideal_time = f"{ideal_time}:00"

        # Build request payload
        payload: dict[str, Any] = {
            "title": title,
            "idealTime": ideal_time,
            "durationMinMins": duration_min_mins,
            "durationMaxMins": duration_max_mins or duration_min_mins,
            "enabled": enabled,
            "recurrence": recurrence,
            "organizer": {"timePolicyType": time_policy_type},
            "eventType": event_type,
            "defenseAggression": defense_aggression,
        }
        if description:
            payload["description"] = description

        habit = await client.post("/api/smart-habits", data=payload)
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return habit
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error creating habit '{title}': {e}")


async def update_habit(
    lineage_id: int,
    title: Optional[str] = None,
    ideal_time: Optional[str] = None,
    duration_min_mins: Optional[int] = None,
    duration_max_mins: Optional[int] = None,
    enabled: Optional[bool] = None,
    frequency: Optional[str] = None,
    ideal_days: Optional[list[str]] = None,
    event_type: Optional[str] = None,
    defense_aggression: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """Update an existing smart habit.

    Args:
        lineage_id: The habit lineage ID to update
        title: New title (optional)
        ideal_time: New preferred time in "HH:MM" format (optional)
        duration_min_mins: New minimum duration in minutes (optional)
        duration_max_mins: New maximum duration in minutes (optional)
        enabled: Enable/disable the habit (optional)
        frequency: New frequency (DAILY, WEEKLY, MONTHLY, YEARLY) (optional)
        ideal_days: New ideal days list (optional)
        event_type: New event type (optional)
        defense_aggression: New defense aggression (optional)
        description: New description (optional)

    Returns:
        Updated habit object.
    """
    try:
        client = _get_client()

        payload: dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if ideal_time is not None:
            # Normalize ideal time to HH:MM:SS format
            if len(ideal_time) == 5:  # HH:MM format
                ideal_time = f"{ideal_time}:00"
            payload["idealTime"] = ideal_time
        if duration_min_mins is not None:
            payload["durationMinMins"] = duration_min_mins
        if duration_max_mins is not None:
            payload["durationMaxMins"] = duration_max_mins
        if enabled is not None:
            payload["enabled"] = enabled
        if description is not None:
            payload["description"] = description
        if event_type is not None:
            payload["eventType"] = event_type
        if defense_aggression is not None:
            payload["defenseAggression"] = defense_aggression

        # Build recurrence object if any recurrence fields provided
        if frequency is not None or ideal_days is not None:
            recurrence: dict[str, Any] = {}
            if frequency is not None:
                recurrence["frequency"] = frequency
            if ideal_days is not None:
                recurrence["idealDays"] = ideal_days
            payload["recurrence"] = recurrence

        habit = await client.patch(f"/api/smart-habits/{lineage_id}", data=payload)
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return habit
    except NotFoundError:
        raise ToolError(f"Habit {lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error updating habit {lineage_id}: {e}")


async def delete_habit(lineage_id: int) -> bool:
    """Delete a smart habit.

    Args:
        lineage_id: The habit lineage ID to delete

    Returns:
        True if deleted successfully.
    """
    try:
        client = _get_client()
        await client.delete(f"/api/smart-habits/{lineage_id}")
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return True
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error deleting habit {lineage_id}: {e}")


async def mark_habit_done(event_id: str) -> dict:
    """Mark a habit instance as done.

    Use this to mark today's scheduled habit event as completed.

    Args:
        event_id: The event ID of the specific habit instance (from list_personal_events)

    Returns:
        Action result with updated events and series info.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/planner/{event_id}/done", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit event {event_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error marking habit done: {e}")


async def skip_habit(event_id: str) -> dict:
    """Skip a habit instance.

    Use this to skip today's scheduled habit event without marking it done.

    Args:
        event_id: The event ID of the specific habit instance to skip

    Returns:
        Action result with updated events and series info.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/planner/{event_id}/skip", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit event {event_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error skipping habit: {e}")


async def lock_habit_instance(event_id: str) -> dict:
    """Lock a habit instance to prevent it from being rescheduled.

    Args:
        event_id: The event ID of the specific habit instance to lock

    Returns:
        Action result with updated events and series info.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/planner/{event_id}/lock", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit event {event_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error locking habit instance: {e}")


async def unlock_habit_instance(event_id: str) -> dict:
    """Unlock a habit instance to allow it to be rescheduled.

    Args:
        event_id: The event ID of the specific habit instance to unlock

    Returns:
        Action result with updated events and series info.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/planner/{event_id}/unlock", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit event {event_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error unlocking habit instance: {e}")


async def start_habit(lineage_id: int) -> dict:
    """Start a habit session now.

    Args:
        lineage_id: The habit lineage ID to start

    Returns:
        Action result with updated events and series info.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/planner/{lineage_id}/start", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit {lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error starting habit {lineage_id}: {e}")


async def stop_habit(lineage_id: int) -> dict:
    """Stop a currently running habit session.

    Args:
        lineage_id: The habit lineage ID to stop

    Returns:
        Action result with updated events and series info.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/planner/{lineage_id}/stop", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit {lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error stopping habit {lineage_id}: {e}")


async def enable_habit(lineage_id: int) -> dict:
    """Enable a disabled habit to resume scheduling.

    Args:
        lineage_id: The habit lineage ID to enable

    Returns:
        Empty dict on success.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/{lineage_id}/enable", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit {lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error enabling habit {lineage_id}: {e}")


async def disable_habit(lineage_id: int) -> bool:
    """Disable a habit to pause scheduling without deleting it.

    Args:
        lineage_id: The habit lineage ID to disable

    Returns:
        True if disabled successfully.
    """
    try:
        client = _get_client()
        await client.delete(f"/api/smart-habits/{lineage_id}/disable")
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return True
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error disabling habit {lineage_id}: {e}")


async def convert_event_to_habit(
    calendar_id: int,
    event_id: str,
    title: str,
    ideal_time: str,
    duration_min_mins: int,
    frequency: str = "WEEKLY",
    ideal_days: Optional[list[str]] = None,
    event_type: str = "SOLO_WORK",
    defense_aggression: str = "DEFAULT",
    duration_max_mins: Optional[int] = None,
    description: Optional[str] = None,
    enabled: bool = True,
    time_policy_type: Optional[str] = None,
) -> dict:
    """Convert a calendar event into a recurring smart habit.

    Note: Not all events can be converted. The API rejects recurring instances,
    all-day events, and multi-day events. Use with short, timed, standalone events.

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to convert
        title: Habit name/title
        ideal_time: Preferred time in "HH:MM" format (e.g., "09:00")
        duration_min_mins: Minimum duration in minutes
        frequency: Recurrence frequency (DAILY, WEEKLY, MONTHLY, YEARLY)
        ideal_days: Days of week for WEEKLY frequency (MONDAY, TUESDAY, etc.)
        event_type: Type of event (FOCUS, SOLO_WORK, PERSONAL, etc.)
        defense_aggression: Protection level (DEFAULT, NONE, LOW, MEDIUM, HIGH, MAX)
        duration_max_mins: Maximum duration in minutes (defaults to min duration)
        description: Optional habit description
        enabled: Whether habit is active (default True)
        time_policy_type: Time policy (WORK, PERSONAL, MEETING). Auto-inferred if not provided.

    Returns:
        Created habit object.
    """
    try:
        client = _get_client()

        # Build recurrence object
        recurrence: dict[str, Any] = {"frequency": frequency}
        if ideal_days:
            recurrence["idealDays"] = ideal_days

        # Determine time policy type based on event type if not explicitly provided
        if time_policy_type is None:
            if event_type == "PERSONAL":
                time_policy_type = "PERSONAL"
            else:
                time_policy_type = "WORK"

        # Normalize ideal time to HH:MM:SS format
        if len(ideal_time) == 5:  # HH:MM format
            ideal_time = f"{ideal_time}:00"

        # Build request payload (same schema as create_habit)
        payload: dict[str, Any] = {
            "title": title,
            "idealTime": ideal_time,
            "durationMinMins": duration_min_mins,
            "durationMaxMins": duration_max_mins or duration_min_mins,
            "enabled": enabled,
            "recurrence": recurrence,
            "organizer": {"timePolicyType": time_policy_type},
            "eventType": event_type,
            "defenseAggression": defense_aggression,
        }
        if description:
            payload["description"] = description

        habit = await client.post(
            f"/api/smart-habits/convert/{calendar_id}/{event_id}",
            data=payload,
        )
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return habit
    except NotFoundError:
        raise ToolError(f"Event {event_id} not found in calendar {calendar_id}")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error converting event to habit: {e}")
