"""Task management tools for Reclaim.ai."""

from typing import Any, Optional

from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


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
    client = _get_client()
    params = {"status": status, "limit": limit}
    tasks = await client.get("/api/tasks", params=params)
    return tasks


async def list_completed_tasks(limit: int = 50) -> list[dict]:
    """List completed and archived tasks from Reclaim.ai.

    Args:
        limit: Maximum number of tasks to return (default 50)

    Returns:
        List of completed/archived task objects.
    """
    client = _get_client()
    params = {"status": "COMPLETE,ARCHIVED", "limit": limit}
    tasks = await client.get("/api/tasks", params=params)
    return tasks


async def get_task(task_id: int) -> dict:
    """Get a single task by ID.

    Args:
        task_id: The task ID to retrieve

    Returns:
        Task object with all details.
    """
    client = _get_client()
    task = await client.get(f"/api/tasks/{task_id}")
    return task


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
        Created task object
    """
    client = _get_client()

    # Convert minutes to time chunks (Reclaim uses 15-min chunks)
    time_chunks = duration_minutes // 15
    if time_chunks < 1:
        time_chunks = 1

    payload: dict[str, Any] = {
        "title": title,
        "timeChunksRequired": time_chunks,
        "minChunkSize": min_chunk_size_minutes,
        "maxChunkSize": max_chunk_size_minutes or duration_minutes,
        "eventCategory": "WORK",
        "priority": priority,
    }

    if due_date is not None:
        payload["deadline"] = due_date
    if snooze_until is not None:
        payload["snoozeUntil"] = snooze_until

    result = await client.post("/api/tasks", payload)
    return result


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
    client = _get_client()

    update_data: dict = {}
    if title is not None:
        update_data["title"] = title
    if duration_minutes is not None:
        update_data["timeChunksRequired"] = duration_minutes // 15
    if due_date is not None:
        update_data["due"] = due_date
    if status is not None:
        update_data["status"] = status

    result = await client.patch(f"/api/tasks/{task_id}", update_data)
    return result


async def mark_task_complete(task_id: int) -> dict:
    """Mark a task as complete.

    Args:
        task_id: The task ID to mark as complete

    Returns:
        Updated task object
    """
    client = _get_client()
    result = await client.post(f"/api/planner/done/task/{task_id}", {})
    return result


async def delete_task(task_id: int) -> bool:
    """Delete a task from Reclaim.ai.

    Args:
        task_id: The task ID to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    client = _get_client()
    result = await client.delete(f"/api/tasks/{task_id}")
    return result


async def add_time_to_task(
    task_id: int,
    minutes: int,
    notes: Optional[str] = None,
) -> dict:
    """Log time spent on a task (increments existing time).

    Args:
        task_id: The task ID
        minutes: Minutes to add to the existing time spent
        notes: Optional notes about the work done

    Returns:
        Updated task object
    """
    client = _get_client()

    # Fetch current task to get existing time spent
    current_task = await client.get(f"/api/tasks/{task_id}")
    current_chunks = current_task.get("timeChunksSpent", 0)

    # Convert minutes to time chunks and add to existing
    new_chunks = minutes // 15
    if new_chunks < 1:
        new_chunks = 1
    total_chunks = current_chunks + new_chunks

    payload: dict[str, Any] = {"timeChunksSpent": total_chunks}
    if notes:
        payload["notes"] = notes

    result = await client.patch(f"/api/tasks/{task_id}", payload)
    return result
