"""Smart Habit tools for Reclaim.ai."""

from typing import Any, Optional

from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


async def list_habits() -> list[dict]:
    """List all smart habits.

    Returns:
        List of SmartHabitLineageView objects with lineageId, title, enabled, etc.
    """
    client = _get_client()
    habits = await client.get("/api/smart-habits")
    return habits


async def get_habit(lineage_id: int) -> dict:
    """Get a single smart habit by lineage ID.

    Args:
        lineage_id: The habit lineage ID to retrieve

    Returns:
        SmartHabitLineageView object with full details.
    """
    client = _get_client()
    habit = await client.get(f"/api/smart-habits/{lineage_id}")
    return habit


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
    """Create a new smart habit.

    Args:
        title: Habit name/title
        ideal_time: Preferred time in "HH:MM" format (e.g., "09:00")
        duration_min_mins: Minimum duration in minutes
        frequency: Recurrence frequency (DAILY, WEEKLY, MONTHLY, YEARLY)
        ideal_days: Days of week for WEEKLY frequency (MONDAY, TUESDAY, etc.)
        event_type: Type of event (FOCUS, SOLO_WORK, PERSONAL, etc.)
        defense_aggression: How aggressively to protect time (DEFAULT, NONE, LOW, MEDIUM, HIGH, MAX)
        duration_max_mins: Maximum duration in minutes (defaults to min duration)
        description: Optional habit description
        enabled: Whether habit is active (default True)
        time_policy_type: Time policy (WORK, PERSONAL, MEETING). Auto-inferred from event_type if not provided.

    Returns:
        Created SmartHabitLineageView object.
    """
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
    return habit


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
        Updated SmartHabitLineageView object.
    """
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
    return habit


async def delete_habit(lineage_id: int) -> bool:
    """Delete a smart habit.

    Args:
        lineage_id: The habit lineage ID to delete

    Returns:
        True if deleted successfully.
    """
    client = _get_client()
    await client.delete(f"/api/smart-habits/{lineage_id}")
    return True


async def mark_habit_done(event_id: str) -> dict:
    """Mark a habit instance as done.

    Args:
        event_id: The event ID of the specific habit instance

    Returns:
        SmartSeriesActionPlannedResult with events, series, and status info.
    """
    client = _get_client()
    result = await client.post(f"/api/smart-habits/planner/{event_id}/done", data={})
    return result


async def skip_habit(event_id: str) -> dict:
    """Skip a habit instance.

    Args:
        event_id: The event ID of the specific habit instance to skip

    Returns:
        SmartSeriesActionPlannedResult with events, series, and status info.
    """
    client = _get_client()
    result = await client.post(f"/api/smart-habits/planner/{event_id}/skip", data={})
    return result
