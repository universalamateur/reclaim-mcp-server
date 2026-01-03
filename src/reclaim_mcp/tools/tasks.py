"""Task management tools for Reclaim.ai."""

from typing import Any, Optional

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from reclaim_mcp.cache import invalidate_cache, ttl_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import NotFoundError, RateLimitError, ReclaimError
from reclaim_mcp.models import ListLimit, TaskCreate, TaskId, TaskListParams, TaskUpdate, TimeLog


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


def _format_validation_errors(e: ValidationError) -> str:
    """Format Pydantic validation errors into a user-friendly message."""
    errors = "; ".join(err["msg"] for err in e.errors())
    return f"Invalid input: {errors}"


@ttl_cache(ttl=60)
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
    # Validate input using Pydantic model
    try:
        validated = TaskListParams(status=status, limit=limit)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        params = {"status": validated.status, "limit": validated.limit}
        tasks = await client.get("/api/tasks", params=params)
        return tasks
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error listing tasks: {e}")


@ttl_cache(ttl=120)
async def list_completed_tasks(limit: int = 50) -> list[dict]:
    """List completed and archived tasks from Reclaim.ai.

    Args:
        limit: Maximum number of tasks to return (default 50)

    Returns:
        List of completed/archived task objects.
    """
    # Validate input using Pydantic model
    try:
        validated = ListLimit(limit=limit)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        params = {"status": "COMPLETE,ARCHIVED", "limit": validated.limit}
        tasks = await client.get("/api/tasks", params=params)
        return tasks
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error listing completed tasks: {e}")


async def get_task(task_id: int) -> dict:
    """Get a single task by ID.

    Args:
        task_id: The task ID to retrieve

    Returns:
        Task object with all details.
    """
    # Validate input using Pydantic model
    try:
        validated = TaskId(task_id=task_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        task = await client.get(f"/api/tasks/{validated.task_id}")
        return task
    except NotFoundError:
        raise ToolError(f"Task {validated.task_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting task {validated.task_id}: {e}")


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
        due_date: ISO datetime string or None for no deadline
        min_chunk_size_minutes: Minimum time block size (default 15)
        max_chunk_size_minutes: Maximum time block size (None = duration)
        snooze_until: Don't schedule before this datetime (ISO format)
        priority: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)

    Returns:
        Created task object.
    """
    # Validate input using Pydantic model
    try:
        validated = TaskCreate(
            title=title,
            duration_minutes=duration_minutes,
            min_chunk_size_minutes=min_chunk_size_minutes,
            max_chunk_size_minutes=max_chunk_size_minutes,
            due_date=due_date,
            snooze_until=snooze_until,
            priority=priority,  # type: ignore[arg-type]
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()

        # Convert minutes to time chunks (Reclaim uses 15-min chunks)
        time_chunks = validated.duration_minutes // 15
        if time_chunks < 1:
            time_chunks = 1

        payload: dict[str, Any] = {
            "title": validated.title,
            "timeChunksRequired": time_chunks,
            "minChunkSize": validated.min_chunk_size_minutes,
            "maxChunkSize": validated.max_chunk_size_minutes or validated.duration_minutes,
            "eventCategory": "WORK",
            "priority": validated.priority.value,
        }

        if validated.due_date is not None:
            payload["deadline"] = validated.due_date
        if validated.snooze_until is not None:
            payload["snoozeUntil"] = validated.snooze_until

        result = await client.post("/api/tasks", payload)
        invalidate_cache("list_tasks")
        invalidate_cache("list_completed_tasks")
        return result
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error creating task '{validated.title}': {e}")


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
        Updated task object.
    """
    # Validate task_id
    try:
        validated_id = TaskId(task_id=task_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    # Validate update fields using Pydantic model
    try:
        validated = TaskUpdate(
            title=title,
            duration_minutes=duration_minutes,
            due_date=due_date,
            status=status,  # type: ignore[arg-type]
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()

        update_data: dict = {}
        if validated.title is not None:
            update_data["title"] = validated.title
        if validated.duration_minutes is not None:
            update_data["timeChunksRequired"] = validated.duration_minutes // 15
        if validated.due_date is not None:
            update_data["due"] = validated.due_date
        if validated.status is not None:
            update_data["status"] = validated.status.value

        result = await client.patch(f"/api/tasks/{validated_id.task_id}", update_data)
        invalidate_cache("list_tasks")
        invalidate_cache("list_completed_tasks")
        return result
    except NotFoundError:
        raise ToolError(f"Task {validated_id.task_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error updating task {validated_id.task_id}: {e}")


async def mark_task_complete(task_id: int) -> dict:
    """Mark a task as complete.

    Args:
        task_id: The task ID to mark as complete

    Returns:
        Updated task object.
    """
    # Validate input using Pydantic model
    try:
        validated = TaskId(task_id=task_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(f"/api/planner/done/task/{validated.task_id}", {})
        invalidate_cache("list_tasks")
        invalidate_cache("list_completed_tasks")
        return result
    except NotFoundError:
        raise ToolError(f"Task {validated.task_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error marking task {validated.task_id} complete: {e}")


async def delete_task(task_id: int) -> bool:
    """Delete a task from Reclaim.ai.

    Args:
        task_id: The task ID to delete

    Returns:
        True if deleted successfully.
    """
    # Validate input using Pydantic model
    try:
        validated = TaskId(task_id=task_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.delete(f"/api/tasks/{validated.task_id}")
        invalidate_cache("list_tasks")
        invalidate_cache("list_completed_tasks")
        return result
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error deleting task {validated.task_id}: {e}")


async def add_time_to_task(
    task_id: int,
    minutes: int,
    notes: Optional[str] = None,
) -> dict:
    """Log time spent on a task using the planner API.

    Args:
        task_id: The task ID
        minutes: Minutes worked on the task
        notes: Optional notes about the work done (stored separately via PATCH)

    Returns:
        Planner action result.
    """
    # Validate task_id
    try:
        validated_id = TaskId(task_id=task_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    # Validate minutes using Pydantic model
    try:
        validated = TimeLog(minutes=minutes)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()

        # Use the dedicated planner endpoint for time logging
        # POST /api/planner/log-work/task/{taskId}?minutes=X
        result = await client.post(
            f"/api/planner/log-work/task/{validated_id.task_id}",
            {},
            params={"minutes": validated.minutes},
        )

        # If notes provided, update them separately on the task
        if notes:
            await client.patch(f"/api/tasks/{validated_id.task_id}", {"notes": notes})

        invalidate_cache("list_tasks")
        return result
    except NotFoundError:
        raise ToolError(f"Task {validated_id.task_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error logging time for task {validated_id.task_id}: {e}")


async def start_task(task_id: int) -> dict:
    """Start working on a task (marks as IN_PROGRESS and starts timer).

    Args:
        task_id: The task ID to start

    Returns:
        Planner action result with updated task state.
    """
    # Validate input using Pydantic model
    try:
        validated = TaskId(task_id=task_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(f"/api/planner/start/task/{validated.task_id}", {})
        invalidate_cache("list_tasks")
        return result
    except NotFoundError:
        raise ToolError(f"Task {validated.task_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error starting task {validated.task_id}: {e}")


async def stop_task(task_id: int) -> dict:
    """Stop working on a task (pauses timer, keeps task active).

    Args:
        task_id: The task ID to stop

    Returns:
        Planner action result with updated task state.
    """
    # Validate input using Pydantic model
    try:
        validated = TaskId(task_id=task_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(f"/api/planner/stop/task/{validated.task_id}", {})
        invalidate_cache("list_tasks")
        return result
    except NotFoundError:
        raise ToolError(f"Task {validated.task_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error stopping task {validated.task_id}: {e}")


async def prioritize_task(task_id: int) -> dict:
    """Prioritize a task (elevates to high priority, triggers rescheduling).

    Args:
        task_id: The task ID to prioritize

    Returns:
        Planner action result with updated task state.
    """
    # Validate input using Pydantic model
    try:
        validated = TaskId(task_id=task_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(f"/api/planner/prioritize/task/{validated.task_id}", {})
        invalidate_cache("list_tasks")
        return result
    except NotFoundError:
        raise ToolError(f"Task {validated.task_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error prioritizing task {validated.task_id}: {e}")


async def restart_task(task_id: int) -> dict:
    """Restart a completed/archived task (returns it to active scheduling).

    Args:
        task_id: The task ID to restart

    Returns:
        Planner action result with updated task state.
    """
    # Validate input using Pydantic model
    try:
        validated = TaskId(task_id=task_id)
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(f"/api/planner/restart/task/{validated.task_id}", {})
        invalidate_cache("list_tasks")
        invalidate_cache("list_completed_tasks")
        return result
    except NotFoundError:
        raise ToolError(f"Task {validated.task_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error restarting task {validated.task_id}: {e}")
