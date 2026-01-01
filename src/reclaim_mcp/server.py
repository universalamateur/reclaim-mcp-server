"""FastMCP server for Reclaim.ai integration."""

from typing import Optional

from fastmcp import FastMCP

from reclaim_mcp.tools import events, habits, tasks

mcp = FastMCP("Reclaim.ai")


@mcp.tool
def health_check() -> str:
    """Check if the server is running."""
    return "OK"


@mcp.tool
async def list_tasks(
    status: str = "NEW,SCHEDULED,IN_PROGRESS",
    limit: int = 50,
) -> list[dict]:
    """List active tasks from Reclaim.ai (excludes completed by default).

    Args:
        status: Comma-separated task statuses (NEW, SCHEDULED, IN_PROGRESS, COMPLETE, ARCHIVED)
        limit: Maximum number of tasks to return (default 50)

    Returns:
        List of task objects with id, title, duration, due_date, status, etc.
    """
    return await tasks.list_tasks(status=status, limit=limit)


@mcp.tool
async def list_completed_tasks(limit: int = 50) -> list[dict]:
    """List completed and archived tasks from Reclaim.ai.

    Args:
        limit: Maximum number of tasks to return (default 50)

    Returns:
        List of completed/archived task objects.
    """
    return await tasks.list_completed_tasks(limit=limit)


@mcp.tool
async def get_task(task_id: int) -> dict:
    """Get a single task by ID.

    Args:
        task_id: The task ID to retrieve

    Returns:
        Task object with all details.
    """
    return await tasks.get_task(task_id=task_id)


@mcp.tool
async def create_task(
    title: str,
    duration_minutes: int,
    due_date: Optional[str] = None,
    min_chunk_size_minutes: int = 15,
    max_chunk_size_minutes: Optional[int] = None,
    snooze_until: Optional[str] = None,
    priority: str = "P2",
) -> dict:
    """Create a new task in Reclaim.ai for auto-scheduling.

    Args:
        title: Task title/description
        duration_minutes: Total time needed for the task in minutes
        due_date: ISO date string (YYYY-MM-DD) or None for no deadline
        min_chunk_size_minutes: Minimum time block size (default 15)
        max_chunk_size_minutes: Maximum time block size (None = duration)
        snooze_until: Don't schedule before this datetime (ISO format)
        priority: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)

    Returns:
        Created task object
    """
    return await tasks.create_task(
        title=title,
        duration_minutes=duration_minutes,
        due_date=due_date,
        min_chunk_size_minutes=min_chunk_size_minutes,
        max_chunk_size_minutes=max_chunk_size_minutes,
        snooze_until=snooze_until,
        priority=priority,
    )


@mcp.tool
async def update_task(
    task_id: int,
    title: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    due_date: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    """Update an existing task in Reclaim.ai.

    Args:
        task_id: The task ID to update
        title: New title (optional)
        duration_minutes: New duration in minutes (optional)
        due_date: New due date in ISO format (optional)
        status: New status - NEW, SCHEDULED, IN_PROGRESS, COMPLETE (optional)

    Returns:
        Updated task object
    """
    return await tasks.update_task(
        task_id=task_id,
        title=title,
        duration_minutes=duration_minutes,
        due_date=due_date,
        status=status,
    )


@mcp.tool
async def mark_task_complete(task_id: int) -> dict:
    """Mark a task as complete.

    Args:
        task_id: The task ID to mark as complete

    Returns:
        Updated task object
    """
    return await tasks.mark_task_complete(task_id=task_id)


@mcp.tool
async def delete_task(task_id: int) -> bool:
    """Delete a task from Reclaim.ai.

    Args:
        task_id: The task ID to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    return await tasks.delete_task(task_id=task_id)


@mcp.tool
async def add_time_to_task(
    task_id: int,
    minutes: int,
    notes: Optional[str] = None,
) -> dict:
    """Log time spent on a task using Reclaim's planner API.

    Args:
        task_id: The task ID
        minutes: Minutes worked on the task
        notes: Optional notes about the work done

    Returns:
        Planner action result confirming time was logged
    """
    return await tasks.add_time_to_task(task_id=task_id, minutes=minutes, notes=notes)


# Calendar & Event Tools (Phase 5)


@mcp.tool
async def list_events(
    start: str,
    end: str,
    calendar_ids: Optional[list[int]] = None,
    event_type: Optional[str] = None,
    thin: bool = True,
) -> list[dict]:
    """List calendar events within a time range.

    Args:
        start: Start date (e.g., '2026-01-02' or '2026-01-02T00:00:00Z' - time is ignored)
        end: End date (e.g., '2026-01-02' or '2026-01-02T23:59:59Z' - time is ignored)
        calendar_ids: Optional list of calendar IDs to filter by
        event_type: Optional event type filter (EXTERNAL, RECLAIM_MANAGED, etc.)
        thin: If True, return minimal event data (default True)

    Returns:
        List of event objects with eventId, title, eventStart, eventEnd, etc.
    """
    return await events.list_events(
        start=start,
        end=end,
        calendar_ids=calendar_ids,
        event_type=event_type,
        thin=thin,
    )


@mcp.tool
async def list_personal_events(
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    """List Reclaim-managed personal events (tasks, habits, focus time).

    Args:
        start: Optional start datetime in ISO format
        end: Optional end datetime in ISO format
        limit: Maximum number of events to return (default 50)

    Returns:
        List of personal event objects.
    """
    return await events.list_personal_events(start=start, end=end, limit=limit)


@mcp.tool
async def get_event(
    calendar_id: int,
    event_id: str,
    thin: bool = False,
) -> dict:
    """Get a single event by calendar ID and event ID.

    Note: Works best with events from list_events (external calendar events).
    Reclaim-managed events from list_personal_events may return 404.

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to retrieve
        thin: If True, return minimal event data (default False for full details)

    Returns:
        Event object with full details.
    """
    return await events.get_event(
        calendar_id=calendar_id,
        event_id=event_id,
        thin=thin,
    )


# Smart Habit Tools (Phase 6)


@mcp.tool
async def list_habits() -> list[dict]:
    """List all smart habits from Reclaim.ai.

    Returns:
        List of habit objects with lineageId, title, enabled, recurrence, etc.
    """
    return await habits.list_habits()


@mcp.tool
async def get_habit(lineage_id: int) -> dict:
    """Get a single smart habit by lineage ID.

    Args:
        lineage_id: The habit lineage ID to retrieve

    Returns:
        SmartHabitLineageView object with full details.
    """
    return await habits.get_habit(lineage_id=lineage_id)


@mcp.tool
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
        defense_aggression: Protection level (DEFAULT, NONE, LOW, MEDIUM, HIGH, MAX) - default DEFAULT
        duration_max_mins: Maximum duration in minutes (defaults to min duration)
        description: Optional habit description
        enabled: Whether habit is active (default True)
        time_policy_type: Time policy (WORK, PERSONAL, MEETING). Auto-inferred if not provided.

    Returns:
        Created habit object.
    """
    return await habits.create_habit(
        title=title,
        ideal_time=ideal_time,
        duration_min_mins=duration_min_mins,
        frequency=frequency,
        ideal_days=ideal_days,
        event_type=event_type,
        defense_aggression=defense_aggression,
        duration_max_mins=duration_max_mins,
        description=description,
        enabled=enabled,
        time_policy_type=time_policy_type,
    )


@mcp.tool
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
    return await habits.update_habit(
        lineage_id=lineage_id,
        title=title,
        ideal_time=ideal_time,
        duration_min_mins=duration_min_mins,
        duration_max_mins=duration_max_mins,
        enabled=enabled,
        frequency=frequency,
        ideal_days=ideal_days,
        event_type=event_type,
        defense_aggression=defense_aggression,
        description=description,
    )


@mcp.tool
async def delete_habit(lineage_id: int) -> bool:
    """Delete a smart habit.

    Args:
        lineage_id: The habit lineage ID to delete

    Returns:
        True if deleted successfully.
    """
    return await habits.delete_habit(lineage_id=lineage_id)


@mcp.tool
async def mark_habit_done(event_id: str) -> dict:
    """Mark a habit instance as done.

    Use this to mark today's scheduled habit event as completed.

    Args:
        event_id: The event ID of the specific habit instance (from list_personal_events)

    Returns:
        Action result with updated events and series info.
    """
    return await habits.mark_habit_done(event_id=event_id)


@mcp.tool
async def skip_habit(event_id: str) -> dict:
    """Skip a habit instance.

    Use this to skip today's scheduled habit event without marking it done.

    Args:
        event_id: The event ID of the specific habit instance to skip

    Returns:
        Action result with updated events and series info.
    """
    return await habits.skip_habit(event_id=event_id)


@mcp.tool
async def lock_habit_instance(event_id: str) -> dict:
    """Lock a habit instance to prevent it from being rescheduled.

    Args:
        event_id: The event ID of the specific habit instance to lock

    Returns:
        Action result with updated events and series info.
    """
    return await habits.lock_habit_instance(event_id=event_id)


@mcp.tool
async def unlock_habit_instance(event_id: str) -> dict:
    """Unlock a habit instance to allow it to be rescheduled.

    Args:
        event_id: The event ID of the specific habit instance to unlock

    Returns:
        Action result with updated events and series info.
    """
    return await habits.unlock_habit_instance(event_id=event_id)


@mcp.tool
async def start_habit(lineage_id: int) -> dict:
    """Start a habit session now.

    Args:
        lineage_id: The habit lineage ID to start

    Returns:
        Action result with updated events and series info.
    """
    return await habits.start_habit(lineage_id=lineage_id)


@mcp.tool
async def stop_habit(lineage_id: int) -> dict:
    """Stop a currently running habit session.

    Args:
        lineage_id: The habit lineage ID to stop

    Returns:
        Action result with updated events and series info.
    """
    return await habits.stop_habit(lineage_id=lineage_id)


@mcp.tool
async def enable_habit(lineage_id: int) -> dict:
    """Enable a disabled habit to resume scheduling.

    Args:
        lineage_id: The habit lineage ID to enable

    Returns:
        Empty dict on success.
    """
    return await habits.enable_habit(lineage_id=lineage_id)


@mcp.tool
async def disable_habit(lineage_id: int) -> bool:
    """Disable a habit to pause scheduling without deleting it.

    Args:
        lineage_id: The habit lineage ID to disable

    Returns:
        True if disabled successfully.
    """
    return await habits.disable_habit(lineage_id=lineage_id)


@mcp.tool
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
        frequency: Recurrence (DAILY, WEEKLY, MONTHLY, YEARLY) - default WEEKLY
        ideal_days: Days for WEEKLY frequency (MONDAY, TUESDAY, etc.)
        event_type: Type (FOCUS, SOLO_WORK, PERSONAL, etc.) - default SOLO_WORK
        defense_aggression: Protection level (DEFAULT, NONE, LOW, MEDIUM, HIGH, MAX) - default DEFAULT
        duration_max_mins: Maximum duration in minutes (defaults to min duration)
        description: Optional habit description
        enabled: Whether habit is active (default True)
        time_policy_type: Time policy (WORK, PERSONAL, MEETING). Auto-inferred if not provided.

    Returns:
        Created habit object.
    """
    return await habits.convert_event_to_habit(
        calendar_id=calendar_id,
        event_id=event_id,
        title=title,
        ideal_time=ideal_time,
        duration_min_mins=duration_min_mins,
        frequency=frequency,
        ideal_days=ideal_days,
        event_type=event_type,
        defense_aggression=defense_aggression,
        duration_max_mins=duration_max_mins,
        description=description,
        enabled=enabled,
        time_policy_type=time_policy_type,
    )


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
