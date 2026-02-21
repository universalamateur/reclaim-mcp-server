"""FastMCP server for Reclaim.ai integration."""

import os
from typing import Any, Callable, Optional, TypeVar

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError

from reclaim_mcp import __version__
from reclaim_mcp.profiles import is_tool_enabled
from reclaim_mcp.tools import analytics, events, focus, habits, tasks

mcp = FastMCP("Reclaim.ai")

# Get profile from environment (validated by pydantic in config.py)
_TOOL_PROFILE = os.getenv("RECLAIM_TOOL_PROFILE", "full").lower()

F = TypeVar("F", bound=Callable[..., Any])


def tool(func: F) -> F:
    """Register a tool only if enabled for the current profile.

    This is a drop-in replacement for @mcp.tool that respects the
    RECLAIM_TOOL_PROFILE environment variable.

    Args:
        func: The tool function to register.

    Returns:
        The function (decorated or not based on profile).
    """
    tool_name = func.__name__
    if is_tool_enabled(tool_name, _TOOL_PROFILE):
        mcp.tool(func)  # Register the tool but don't return the wrapped version
    # Always return the original function to satisfy type checker
    return func


@tool
def health_check() -> str:
    """Check if the server is running."""
    return f"OK (v{__version__})"


@tool
async def verify_connection() -> dict:
    """Verify API connection by fetching current user info.

    Returns:
        Connection status with user details (id, email, name).
    """
    try:
        from reclaim_mcp.client import ReclaimClient
        from reclaim_mcp.config import get_settings

        settings = get_settings()
        client = ReclaimClient(settings)
        user = await client.get("/api/users/current")
        return {
            "status": "connected",
            "user_id": user.get("id"),
            "email": user.get("email"),
            "name": user.get("name"),
        }
    except Exception as e:
        raise ToolError(f"Connection failed: {e}")


# Task Tools


@tool
async def list_tasks(
    ctx: Context,
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
    await ctx.info(f"Listing tasks: status={status}, limit={limit}")
    return await tasks.list_tasks(status=status, limit=limit)


@tool
async def list_completed_tasks(ctx: Context, limit: int = 50) -> list[dict]:
    """List completed and archived tasks from Reclaim.ai.

    Args:
        limit: Maximum number of tasks to return (default 50)

    Returns:
        List of completed/archived task objects.
    """
    await ctx.info(f"Listing completed tasks: limit={limit}")
    return await tasks.list_completed_tasks(limit=limit)


@tool
async def get_task(ctx: Context, task_id: int) -> dict:
    """Get a single task by ID.

    Args:
        task_id: The task ID to retrieve

    Returns:
        Task object with all details.
    """
    await ctx.info(f"Getting task: id={task_id}")
    return await tasks.get_task(task_id=task_id)


@tool
async def create_task(
    ctx: Context,
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
    await ctx.info(f"Creating task: '{title}' ({duration_minutes}min, {priority})")
    return await tasks.create_task(
        title=title,
        duration_minutes=duration_minutes,
        due_date=due_date,
        min_chunk_size_minutes=min_chunk_size_minutes,
        max_chunk_size_minutes=max_chunk_size_minutes,
        snooze_until=snooze_until,
        priority=priority,
    )


@tool
async def update_task(
    ctx: Context,
    task_id: int,
    title: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    due_date: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    snooze_until: Optional[str] = None,
    notes: Optional[str] = None,
    min_chunk_size_minutes: Optional[int] = None,
    max_chunk_size_minutes: Optional[int] = None,
) -> dict:
    """Update an existing task in Reclaim.ai.

    Args:
        task_id: The task ID to update
        title: New title (optional)
        duration_minutes: New duration in minutes (optional)
        due_date: New due date in YYYY-MM-DD format (optional)
        status: New status - NEW, SCHEDULED, IN_PROGRESS, COMPLETE (optional)
        priority: New priority - P1 (Critical), P2 (High), P3 (Medium), P4 (Low) (optional)
        snooze_until: Don't schedule before this datetime, ISO format (optional)
        notes: Update task notes (optional)
        min_chunk_size_minutes: Minimum time block size in minutes (optional)
        max_chunk_size_minutes: Maximum time block size in minutes (optional)

    Returns:
        Updated task object
    """
    await ctx.info(f"Updating task: id={task_id}")
    return await tasks.update_task(
        task_id=task_id,
        title=title,
        duration_minutes=duration_minutes,
        due_date=due_date,
        status=status,
        priority=priority,
        snooze_until=snooze_until,
        notes=notes,
        min_chunk_size_minutes=min_chunk_size_minutes,
        max_chunk_size_minutes=max_chunk_size_minutes,
    )


@tool
async def mark_task_complete(ctx: Context, task_id: int) -> dict:
    """Mark a task as complete.

    Args:
        task_id: The task ID to mark as complete

    Returns:
        Updated task object
    """
    await ctx.info(f"Marking task complete: id={task_id}")
    return await tasks.mark_task_complete(task_id=task_id)


@tool
async def delete_task(ctx: Context, task_id: int) -> bool:
    """Delete a task from Reclaim.ai.

    Args:
        task_id: The task ID to delete

    Returns:
        True if deleted successfully
    """
    await ctx.info(f"Deleting task: id={task_id}")
    return await tasks.delete_task(task_id=task_id)


@tool
async def add_time_to_task(
    ctx: Context,
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
    await ctx.info(f"Logging time to task: id={task_id}, minutes={minutes}")
    return await tasks.add_time_to_task(task_id=task_id, minutes=minutes, notes=notes)


@tool
async def start_task(ctx: Context, task_id: int) -> dict:
    """Start working on a task (marks as IN_PROGRESS and starts timer).

    Args:
        task_id: The task ID to start working on

    Returns:
        Planner action result with updated task state
    """
    await ctx.info(f"Starting task: id={task_id}")
    return await tasks.start_task(task_id=task_id)


@tool
async def stop_task(ctx: Context, task_id: int) -> dict:
    """Stop working on a task (pauses timer, keeps task active).

    Args:
        task_id: The task ID to stop working on

    Returns:
        Planner action result with updated task state
    """
    await ctx.info(f"Stopping task: id={task_id}")
    return await tasks.stop_task(task_id=task_id)


@tool
async def prioritize_task(ctx: Context, task_id: int) -> dict:
    """Prioritize a task (elevates to high priority, triggers rescheduling).

    Args:
        task_id: The task ID to prioritize

    Returns:
        Planner action result with updated task state
    """
    await ctx.info(f"Prioritizing task: id={task_id}")
    return await tasks.prioritize_task(task_id=task_id)


@tool
async def restart_task(ctx: Context, task_id: int) -> dict:
    """Restart a completed/archived task (returns it to active scheduling).

    Args:
        task_id: The task ID to restart

    Returns:
        Planner action result with updated task state
    """
    await ctx.info(f"Restarting task: id={task_id}")
    return await tasks.restart_task(task_id=task_id)


# Calendar & Event Tools


@tool
async def list_events(
    ctx: Context,
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
    await ctx.info(f"Listing events: start={start}, end={end}")
    return await events.list_events(
        start=start,
        end=end,
        calendar_ids=calendar_ids,
        event_type=event_type,
        thin=thin,
    )


@tool
async def list_personal_events(
    ctx: Context,
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
    await ctx.info(f"Listing personal events: limit={limit}")
    return await events.list_personal_events(start=start, end=end, limit=limit)


@tool
async def get_event(
    ctx: Context,
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
    await ctx.info(f"Getting event: calendar_id={calendar_id}, event_id={event_id}")
    return await events.get_event(
        calendar_id=calendar_id,
        event_id=event_id,
        thin=thin,
    )


@tool
async def set_event_rsvp(
    ctx: Context,
    calendar_id: int,
    event_id: str,
    rsvp_status: str,
    send_updates: bool = True,
) -> dict:
    """Set RSVP status for a calendar event.

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to update RSVP for
        rsvp_status: RSVP status (ACCEPTED, DECLINED, TENTATIVE, NEEDS_ACTION)
        send_updates: Whether to send update notifications (default True)

    Returns:
        Planner action result with updated event state.
    """
    await ctx.info(f"Setting RSVP: {calendar_id}/{event_id} -> {rsvp_status}")
    return await events.set_event_rsvp(
        calendar_id=calendar_id,
        event_id=event_id,
        rsvp_status=rsvp_status,
        send_updates=send_updates,
    )


@tool
async def move_event(
    ctx: Context,
    event_id: str,
    start_time: str,
    end_time: str,
) -> dict:
    """Move/reschedule an event to a new time.

    Args:
        event_id: The event ID to move
        start_time: New start time in ISO format (e.g., '2026-01-02T14:00:00Z')
        end_time: New end time in ISO format (e.g., '2026-01-02T15:00:00Z')

    Returns:
        Planner action result with updated event state.
    """
    await ctx.info(f"Moving event: event_id={event_id}")
    return await events.move_event(
        event_id=event_id,
        start_time=start_time,
        end_time=end_time,
    )


# Smart Habit Tools


@tool
async def list_habits(ctx: Context) -> list[dict]:
    """List all smart habits from Reclaim.ai.

    Returns:
        List of habit objects with lineageId, title, enabled, recurrence, etc.
    """
    await ctx.info("Listing habits")
    return await habits.list_habits()


@tool
async def get_habit(ctx: Context, lineage_id: int) -> dict:
    """Get a single smart habit by lineage ID.

    Args:
        lineage_id: The habit lineage ID to retrieve

    Returns:
        SmartHabitLineageView object with full details.
    """
    await ctx.info(f"Getting habit: lineage_id={lineage_id}")
    return await habits.get_habit(lineage_id=lineage_id)


@tool
async def create_habit(
    ctx: Context,
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
    await ctx.info(f"Creating habit: '{title}' at {ideal_time} ({frequency})")
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


@tool
async def update_habit(
    ctx: Context,
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
    await ctx.info(f"Updating habit: lineage_id={lineage_id}")
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


@tool
async def delete_habit(ctx: Context, lineage_id: int) -> bool:
    """Delete a smart habit.

    Args:
        lineage_id: The habit lineage ID to delete

    Returns:
        True if deleted successfully.
    """
    await ctx.info(f"Deleting habit: lineage_id={lineage_id}")
    return await habits.delete_habit(lineage_id=lineage_id)


@tool
async def mark_habit_done(ctx: Context, event_id: str) -> dict:
    """Mark a habit instance as done.

    Use this to mark today's scheduled habit event as completed.

    Args:
        event_id: The event ID of the specific habit instance (from list_personal_events)

    Returns:
        Action result with updated events and series info.
    """
    await ctx.info(f"Marking habit done: event_id={event_id}")
    return await habits.mark_habit_done(event_id=event_id)


@tool
async def skip_habit(ctx: Context, event_id: str) -> dict:
    """Skip a habit instance.

    Use this to skip today's scheduled habit event without marking it done.

    Args:
        event_id: The event ID of the specific habit instance to skip

    Returns:
        Action result with updated events and series info.
    """
    await ctx.info(f"Skipping habit: event_id={event_id}")
    return await habits.skip_habit(event_id=event_id)


@tool
async def lock_habit_instance(ctx: Context, event_id: str) -> dict:
    """Lock a habit instance to prevent it from being rescheduled.

    Args:
        event_id: The event ID of the specific habit instance to lock

    Returns:
        Action result with updated events and series info.
    """
    await ctx.info(f"Locking habit instance: event_id={event_id}")
    return await habits.lock_habit_instance(event_id=event_id)


@tool
async def unlock_habit_instance(ctx: Context, event_id: str) -> dict:
    """Unlock a habit instance to allow it to be rescheduled.

    Args:
        event_id: The event ID of the specific habit instance to unlock

    Returns:
        Action result with updated events and series info.
    """
    await ctx.info(f"Unlocking habit instance: event_id={event_id}")
    return await habits.unlock_habit_instance(event_id=event_id)


@tool
async def start_habit(ctx: Context, lineage_id: int) -> dict:
    """Start a habit session now.

    Args:
        lineage_id: The habit lineage ID to start

    Returns:
        Action result with updated events and series info.
    """
    await ctx.info(f"Starting habit: lineage_id={lineage_id}")
    return await habits.start_habit(lineage_id=lineage_id)


@tool
async def stop_habit(ctx: Context, lineage_id: int) -> dict:
    """Stop a currently running habit session.

    Args:
        lineage_id: The habit lineage ID to stop

    Returns:
        Action result with updated events and series info.
    """
    await ctx.info(f"Stopping habit: lineage_id={lineage_id}")
    return await habits.stop_habit(lineage_id=lineage_id)


@tool
async def enable_habit(ctx: Context, lineage_id: int) -> dict:
    """Enable a disabled habit to resume scheduling.

    Args:
        lineage_id: The habit lineage ID to enable

    Returns:
        Empty dict on success.
    """
    await ctx.info(f"Enabling habit: lineage_id={lineage_id}")
    return await habits.enable_habit(lineage_id=lineage_id)


@tool
async def disable_habit(ctx: Context, lineage_id: int) -> bool:
    """Disable a habit to pause scheduling without deleting it.

    Args:
        lineage_id: The habit lineage ID to disable

    Returns:
        True if disabled successfully.
    """
    await ctx.info(f"Disabling habit: lineage_id={lineage_id}")
    return await habits.disable_habit(lineage_id=lineage_id)


@tool
async def convert_event_to_habit(
    ctx: Context,
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
        defense_aggression: Protection level (DEFAULT, NONE, LOW, MEDIUM, HIGH, MAX)
        duration_max_mins: Maximum duration in minutes (defaults to min duration)
        description: Optional habit description
        enabled: Whether habit is active (default True)
        time_policy_type: Time policy (WORK, PERSONAL, MEETING). Auto-inferred if not provided.

    Returns:
        Created habit object.
    """
    await ctx.info(f"Converting event to habit: {calendar_id}/{event_id} -> '{title}'")
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


# Analytics Tools


@tool
async def get_user_analytics(
    ctx: Context,
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

    Returns:
        Analytics data with time breakdowns by category.
    """
    await ctx.info(f"Getting user analytics: start={start}, end={end}, metric={metric_name}")
    return await analytics.get_user_analytics(
        start=start,
        end=end,
        metric_name=metric_name,
    )


@tool
async def get_focus_insights(
    ctx: Context,
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
    await ctx.info(f"Getting focus insights: start={start}, end={end}")
    return await analytics.get_focus_insights(start=start, end=end)


# Focus Time Tools


@tool
async def get_focus_settings(ctx: Context) -> list[dict]:
    """Get current focus time settings for the user.

    Returns:
        List of focus settings objects (one per focus type).
    """
    await ctx.info("Getting focus settings")
    return await focus.get_focus_settings()


@tool
async def update_focus_settings(
    ctx: Context,
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
    await ctx.info(f"Updating focus settings: id={settings_id}")
    return await focus.update_focus_settings(
        settings_id=settings_id,
        min_duration_mins=min_duration_mins,
        ideal_duration_mins=ideal_duration_mins,
        max_duration_mins=max_duration_mins,
        defense_aggression=defense_aggression,
        enabled=enabled,
    )


@tool
async def lock_focus_block(
    ctx: Context,
    calendar_id: int,
    event_id: str,
) -> dict:
    """Lock a focus time block to prevent it from being rescheduled.

    Args:
        calendar_id: The calendar ID containing the focus block
        event_id: The focus block event ID to lock

    Returns:
        Planner action result with updated event state.
    """
    await ctx.info(f"Locking focus block: calendar_id={calendar_id}, event_id={event_id}")
    return await focus.lock_focus_block(calendar_id=calendar_id, event_id=event_id)


@tool
async def unlock_focus_block(
    ctx: Context,
    calendar_id: int,
    event_id: str,
) -> dict:
    """Unlock a focus time block to allow it to be rescheduled.

    Args:
        calendar_id: The calendar ID containing the focus block
        event_id: The focus block event ID to unlock

    Returns:
        Planner action result with updated event state.
    """
    await ctx.info(f"Unlocking focus block: calendar_id={calendar_id}, event_id={event_id}")
    return await focus.unlock_focus_block(calendar_id=calendar_id, event_id=event_id)


@tool
async def reschedule_focus_block(
    ctx: Context,
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
    await ctx.info(f"Rescheduling focus block: calendar_id={calendar_id}, event_id={event_id}")
    return await focus.reschedule_focus_block(
        calendar_id=calendar_id,
        event_id=event_id,
        start_time=start_time,
        end_time=end_time,
    )


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
