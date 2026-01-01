"""FastMCP server for Reclaim.ai integration."""

from typing import Optional

from fastmcp import FastMCP

from reclaim_mcp.tools import tasks

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


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
