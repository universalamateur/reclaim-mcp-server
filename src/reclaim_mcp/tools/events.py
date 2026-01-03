"""Calendar and event tools for Reclaim.ai."""

from datetime import datetime, timedelta
from typing import Any, Optional

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from reclaim_mcp.cache import invalidate_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import NotFoundError, RateLimitError, ReclaimError
from reclaim_mcp.models import EventMove, EventRsvp


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


def _format_validation_errors(e: ValidationError) -> str:
    """Format Pydantic validation errors into a user-friendly message."""
    errors = "; ".join(err["msg"] for err in e.errors())
    return f"Invalid input: {errors}"


def _extract_date(datetime_str: str) -> str:
    """Extract date part (YYYY-MM-DD) from datetime string.

    Handles both date-only ('2026-01-02') and datetime ('2026-01-02T00:00:00Z') formats.
    """
    # Take first 10 characters (YYYY-MM-DD)
    return datetime_str[:10]


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
    try:
        client = _get_client()
        params: dict[str, Any] = {
            "start": _extract_date(start),
            "end": _extract_date(end),
            "thin": thin,
        }
        if calendar_ids:
            params["calendarIds"] = ",".join(str(c) for c in calendar_ids)
        if event_type:
            params["type"] = event_type

        events = await client.get("/api/events", params=params)
        return events
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error listing events: {e}")


async def list_personal_events(
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    """List Reclaim-managed personal events (tasks, habits, focus time).

    Args:
        start: Optional start datetime in ISO format (defaults to today)
        end: Optional end datetime in ISO format (defaults to 7 days from now)
        limit: Maximum number of events to return (default 50)

    Returns:
        List of personal event objects.
    """
    # Default to current week if dates not provided
    if start is None:
        start = datetime.now().strftime("%Y-%m-%d")
    if end is None:
        end_date = datetime.now() + timedelta(days=7)
        end = end_date.strftime("%Y-%m-%d")

    try:
        client = _get_client()
        params: dict[str, Any] = {
            "limit": limit,
            "start": _extract_date(start),
            "end": _extract_date(end),
        }

        events = await client.get("/api/events/personal", params=params)
        return events
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error listing personal events: {e}")


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
    try:
        client = _get_client()
        params: dict[str, Any] = {"thin": thin}
        event = await client.get(f"/api/events/{calendar_id}/{event_id}", params=params)
        return event
    except NotFoundError:
        raise ToolError(f"Event {event_id} not found in calendar {calendar_id}")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting event {event_id}: {e}")


async def pin_event(calendar_id: int, event_id: str) -> dict:
    """Pin an event to lock it at its current time (prevents rescheduling).

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to pin

    Returns:
        Planner action result with updated event state.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/planner/event/{calendar_id}/{event_id}/pin", {})
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(f"Event {event_id} not found in calendar {calendar_id}")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error pinning event {event_id}: {e}")


async def unpin_event(calendar_id: int, event_id: str) -> dict:
    """Unpin an event to allow it to be rescheduled by the AI.

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to unpin

    Returns:
        Planner action result with updated event state.
    """
    try:
        client = _get_client()
        result = await client.post(f"/api/planner/event/{calendar_id}/{event_id}/unpin", {})
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(f"Event {event_id} not found in calendar {calendar_id}")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error unpinning event {event_id}: {e}")


async def set_event_rsvp(
    calendar_id: int,
    event_id: str,
    rsvp_status: str,
) -> dict:
    """Set RSVP status for a calendar event.

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to update RSVP for
        rsvp_status: RSVP status (ACCEPTED, DECLINED, TENTATIVE, NEEDS_ACTION)

    Returns:
        Planner action result with updated event state.
    """
    # Validate input using Pydantic model
    try:
        validated = EventRsvp(
            calendar_id=calendar_id,
            event_id=event_id,
            rsvp_status=rsvp_status,  # type: ignore[arg-type]
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(
            f"/api/planner/event/rsvp/{validated.calendar_id}/{validated.event_id}",
            {"rsvpStatus": validated.rsvp_status.value},
        )
        invalidate_cache("list_events")
        return result
    except NotFoundError:
        raise ToolError(f"Event {event_id} not found in calendar {calendar_id}")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error setting RSVP for event {event_id}: {e}")


async def move_event(
    calendar_id: int,
    event_id: str,
    start_time: str,
    end_time: str,
) -> dict:
    """Move/reschedule an event to a new time.

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to move
        start_time: New start time in ISO format (e.g., '2026-01-02T14:00:00Z')
        end_time: New end time in ISO format (e.g., '2026-01-02T15:00:00Z')

    Returns:
        Planner action result with updated event state.
    """
    # Validate input using Pydantic model
    try:
        validated = EventMove(
            calendar_id=calendar_id,
            event_id=event_id,
            start_time=start_time,
            end_time=end_time,
        )
    except ValidationError as e:
        raise ToolError(_format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(
            f"/api/planner/event/{validated.calendar_id}/{validated.event_id}/move",
            {"start": validated.start_time, "end": validated.end_time},
        )
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(f"Event {event_id} not found in calendar {calendar_id}")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error moving event {event_id}: {e}")
