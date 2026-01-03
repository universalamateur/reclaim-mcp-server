"""Smart Habit tools for Reclaim.ai."""

from typing import Any, Optional

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from reclaim_mcp.cache import invalidate_cache, ttl_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import NotFoundError, RateLimitError, ReclaimError
from reclaim_mcp.models import CalendarEventId, EventInstanceId, HabitCreate, HabitId, HabitUpdate


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


def _format_validation_errors(e: ValidationError) -> str:
    """Format Pydantic validation errors into a user-friendly message."""
    errors = "; ".join(err["msg"] for err in e.errors())
    return f"Invalid input: {errors}"


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
    # Validate input using Pydantic model
    try:
        validated = HabitId(lineage_id=lineage_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        habit = await client.get(f"/api/smart-habits/{validated.lineage_id}")
        return habit
    except NotFoundError:
        raise ToolError(f"Habit {validated.lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting habit {validated.lineage_id}: {e}")


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
    # Validate input using Pydantic model
    try:
        validated = HabitCreate(
            title=title,
            ideal_time=ideal_time,
            duration_min_mins=duration_min_mins,
            duration_max_mins=duration_max_mins,
            frequency=frequency,  # type: ignore[arg-type]
            ideal_days=ideal_days,  # type: ignore[arg-type]
            event_type=event_type,  # type: ignore[arg-type]
            defense_aggression=defense_aggression,  # type: ignore[arg-type]
            description=description,
            enabled=enabled,
            time_policy_type=time_policy_type,  # type: ignore[arg-type]
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()

        # Build recurrence object
        recurrence: dict[str, Any] = {"frequency": validated.frequency.value}
        if validated.ideal_days:
            recurrence["idealDays"] = [d.value for d in validated.ideal_days]

        # Determine time policy type based on event type if not explicitly provided
        time_policy = validated.time_policy_type
        if time_policy is None:
            if validated.event_type.value == "PERSONAL":
                time_policy_str = "PERSONAL"
            else:
                time_policy_str = "WORK"
        else:
            time_policy_str = time_policy.value

        # Normalize ideal time to HH:MM:SS format
        ideal_time_normalized = validated.ideal_time
        if len(ideal_time_normalized) == 5:  # HH:MM format
            ideal_time_normalized = f"{ideal_time_normalized}:00"

        # Build request payload
        payload: dict[str, Any] = {
            "title": validated.title,
            "idealTime": ideal_time_normalized,
            "durationMinMins": validated.duration_min_mins,
            "durationMaxMins": validated.duration_max_mins or validated.duration_min_mins,
            "enabled": validated.enabled,
            "recurrence": recurrence,
            "organizer": {"timePolicyType": time_policy_str},
            "eventType": validated.event_type.value,
            "defenseAggression": validated.defense_aggression.value,
        }
        if validated.description:
            payload["description"] = validated.description

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
    # Validate lineage_id
    try:
        validated_id = HabitId(lineage_id=lineage_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    # Validate update fields using Pydantic model
    try:
        validated = HabitUpdate(
            title=title,
            ideal_time=ideal_time,
            duration_min_mins=duration_min_mins,
            duration_max_mins=duration_max_mins,
            enabled=enabled,
            frequency=frequency,  # type: ignore[arg-type]
            ideal_days=ideal_days,  # type: ignore[arg-type]
            event_type=event_type,  # type: ignore[arg-type]
            defense_aggression=defense_aggression,  # type: ignore[arg-type]
            description=description,
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()

        payload: dict[str, Any] = {}
        if validated.title is not None:
            payload["title"] = validated.title
        if validated.ideal_time is not None:
            # Normalize ideal time to HH:MM:SS format
            ideal_time_normalized = validated.ideal_time
            if len(ideal_time_normalized) == 5:  # HH:MM format
                ideal_time_normalized = f"{ideal_time_normalized}:00"
            payload["idealTime"] = ideal_time_normalized
        if validated.duration_min_mins is not None:
            payload["durationMinMins"] = validated.duration_min_mins
        if validated.duration_max_mins is not None:
            payload["durationMaxMins"] = validated.duration_max_mins
        if validated.enabled is not None:
            payload["enabled"] = validated.enabled
        if validated.description is not None:
            payload["description"] = validated.description
        if validated.event_type is not None:
            payload["eventType"] = validated.event_type.value
        if validated.defense_aggression is not None:
            payload["defenseAggression"] = validated.defense_aggression.value

        # Build recurrence object if any recurrence fields provided
        if validated.frequency is not None or validated.ideal_days is not None:
            recurrence: dict[str, Any] = {}
            if validated.frequency is not None:
                recurrence["frequency"] = validated.frequency.value
            if validated.ideal_days is not None:
                recurrence["idealDays"] = [d.value for d in validated.ideal_days]
            payload["recurrence"] = recurrence

        habit = await client.patch(f"/api/smart-habits/{validated_id.lineage_id}", data=payload)
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return habit
    except NotFoundError:
        raise ToolError(f"Habit {validated_id.lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error updating habit {validated_id.lineage_id}: {e}")


async def delete_habit(lineage_id: int) -> bool:
    """Delete a smart habit.

    Args:
        lineage_id: The habit lineage ID to delete

    Returns:
        True if deleted successfully.
    """
    # Validate input using Pydantic model
    try:
        validated = HabitId(lineage_id=lineage_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        await client.delete(f"/api/smart-habits/{validated.lineage_id}")
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return True
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error deleting habit {validated.lineage_id}: {e}")


async def mark_habit_done(event_id: str) -> dict:
    """Mark a habit instance as done.

    Use this to mark today's scheduled habit event as completed.

    Args:
        event_id: The event ID of the specific habit instance (from list_personal_events)

    Returns:
        Action result with updated events and series info.
    """
    # Validate input using Pydantic model
    try:
        validated = EventInstanceId(event_id=event_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/planner/{validated.event_id}/done", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit event {validated.event_id} not found")
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
    # Validate input using Pydantic model
    try:
        validated = EventInstanceId(event_id=event_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/planner/{validated.event_id}/skip", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit event {validated.event_id} not found")
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
    # Validate input using Pydantic model
    try:
        validated = EventInstanceId(event_id=event_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/planner/{validated.event_id}/lock", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit event {validated.event_id} not found")
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
    # Validate input using Pydantic model
    try:
        validated = EventInstanceId(event_id=event_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(
            f"/api/smart-habits/planner/{validated.event_id}/unlock", data={}
        )
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit event {validated.event_id} not found")
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
    # Validate input using Pydantic model
    try:
        validated = HabitId(lineage_id=lineage_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(
            f"/api/smart-habits/planner/{validated.lineage_id}/start", data={}
        )
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit {validated.lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error starting habit {validated.lineage_id}: {e}")


async def stop_habit(lineage_id: int) -> dict:
    """Stop a currently running habit session.

    Args:
        lineage_id: The habit lineage ID to stop

    Returns:
        Action result with updated events and series info.
    """
    # Validate input using Pydantic model
    try:
        validated = HabitId(lineage_id=lineage_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(
            f"/api/smart-habits/planner/{validated.lineage_id}/stop", data={}
        )
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit {validated.lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error stopping habit {validated.lineage_id}: {e}")


async def enable_habit(lineage_id: int) -> dict:
    """Enable a disabled habit to resume scheduling.

    Args:
        lineage_id: The habit lineage ID to enable

    Returns:
        Empty dict on success.
    """
    # Validate input using Pydantic model
    try:
        validated = HabitId(lineage_id=lineage_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(f"/api/smart-habits/{validated.lineage_id}/enable", data={})
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return result
    except NotFoundError:
        raise ToolError(f"Habit {validated.lineage_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error enabling habit {validated.lineage_id}: {e}")


async def disable_habit(lineage_id: int) -> bool:
    """Disable a habit to pause scheduling without deleting it.

    Args:
        lineage_id: The habit lineage ID to disable

    Returns:
        True if disabled successfully.
    """
    # Validate input using Pydantic model
    try:
        validated = HabitId(lineage_id=lineage_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        await client.delete(f"/api/smart-habits/{validated.lineage_id}/disable")
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return True
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error disabling habit {validated.lineage_id}: {e}")


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
    # Validate calendar/event IDs using Pydantic model
    try:
        validated_event = CalendarEventId(calendar_id=calendar_id, event_id=event_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    # Validate habit fields using Pydantic model
    try:
        validated = HabitCreate(
            title=title,
            ideal_time=ideal_time,
            duration_min_mins=duration_min_mins,
            duration_max_mins=duration_max_mins,
            frequency=frequency,  # type: ignore[arg-type]
            ideal_days=ideal_days,  # type: ignore[arg-type]
            event_type=event_type,  # type: ignore[arg-type]
            defense_aggression=defense_aggression,  # type: ignore[arg-type]
            description=description,
            enabled=enabled,
            time_policy_type=time_policy_type,  # type: ignore[arg-type]
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()

        # Build recurrence object
        recurrence: dict[str, Any] = {"frequency": validated.frequency.value}
        if validated.ideal_days:
            recurrence["idealDays"] = [d.value for d in validated.ideal_days]

        # Determine time policy type based on event type if not explicitly provided
        time_policy = validated.time_policy_type
        if time_policy is None:
            if validated.event_type.value == "PERSONAL":
                time_policy_str = "PERSONAL"
            else:
                time_policy_str = "WORK"
        else:
            time_policy_str = time_policy.value

        # Normalize ideal time to HH:MM:SS format
        ideal_time_normalized = validated.ideal_time
        if len(ideal_time_normalized) == 5:  # HH:MM format
            ideal_time_normalized = f"{ideal_time_normalized}:00"

        # Build request payload (same schema as create_habit)
        payload: dict[str, Any] = {
            "title": validated.title,
            "idealTime": ideal_time_normalized,
            "durationMinMins": validated.duration_min_mins,
            "durationMaxMins": validated.duration_max_mins or validated.duration_min_mins,
            "enabled": validated.enabled,
            "recurrence": recurrence,
            "organizer": {"timePolicyType": time_policy_str},
            "eventType": validated.event_type.value,
            "defenseAggression": validated.defense_aggression.value,
        }
        if validated.description:
            payload["description"] = validated.description

        habit = await client.post(
            f"/api/smart-habits/convert/{validated_event.calendar_id}/{validated_event.event_id}",
            data=payload,
        )
        invalidate_cache("list_habits")
        invalidate_cache("get_habit")
        return habit
    except NotFoundError:
        raise ToolError(
            f"Event {validated_event.event_id} not found in calendar "
            f"{validated_event.calendar_id}"
        )
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error converting event to habit: {e}")
