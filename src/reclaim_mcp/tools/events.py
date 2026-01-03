"""Calendar and event tools for Reclaim.ai."""

from datetime import datetime, timedelta
from typing import Any, Optional

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from reclaim_mcp.cache import invalidate_cache
from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings
from reclaim_mcp.exceptions import NotFoundError, RateLimitError, ReclaimError
from reclaim_mcp.utils import format_validation_errors

from reclaim_mcp.models import (  # isort: skip
    CalendarEventId,
    DateRange,
    EventMove,
    EventRsvp,
    ListLimit,
    OptionalDateRange,
)


def _get_client() -> ReclaimClient:
    """Get a configured Reclaim client."""
    settings = get_settings()
    return ReclaimClient(settings)


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
    # Validate input using Pydantic model
    try:
        validated = DateRange(start=_extract_date(start), end=_extract_date(end))
    except ValidationError as e:
        raise ToolError(format_validation_errors(e))

    try:
        client = _get_client()
        params: dict[str, Any] = {
            "start": validated.start,
            "end": validated.end,
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
    # Validate limit using Pydantic model
    try:
        validated_limit = ListLimit(limit=limit)
    except ValidationError as e:
        raise ToolError(format_validation_errors(e))

    # Default to current week if dates not provided
    start_date = start
    end_date = end
    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")
    if end_date is None:
        end_dt = datetime.now() + timedelta(days=7)
        end_date = end_dt.strftime("%Y-%m-%d")

    # Validate dates using Pydantic model
    try:
        validated_dates = OptionalDateRange(
            start=_extract_date(start_date),
            end=_extract_date(end_date),
        )
    except ValidationError as e:
        raise ToolError(format_validation_errors(e))

    try:
        client = _get_client()
        params: dict[str, Any] = {
            "limit": validated_limit.limit,
            "start": validated_dates.start,
            "end": validated_dates.end,
        }

        events = await client.get("/api/events/personal", params=params)
        return events
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error listing personal events: {e}")
    except Exception as e:
        # Catch unexpected errors to help diagnose issues like the limit>17 bug
        raise ToolError(f"Unexpected error listing personal events: {type(e).__name__}: {e}")


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
    # Validate input using Pydantic model
    try:
        validated = CalendarEventId(calendar_id=calendar_id, event_id=event_id)
    except ValidationError as e:
        raise ToolError(format_validation_errors(e))

    try:
        client = _get_client()
        params: dict[str, Any] = {"thin": thin}
        event = await client.get(
            f"/api/events/{validated.calendar_id}/{validated.event_id}",
            params=params,
        )
        return event
    except NotFoundError:
        # fmt: off
        raise ToolError(
            f"Event {validated.event_id} not found in calendar "
            f"{validated.calendar_id}"
        )
        # fmt: on
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error getting event {validated.event_id}: {e}")


async def pin_event(calendar_id: int, event_id: str) -> dict:
    """Pin an event to lock it at its current time (prevents rescheduling).

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to pin

    Returns:
        Planner action result with updated event state.
    """
    # Validate input using Pydantic model
    try:
        validated = CalendarEventId(calendar_id=calendar_id, event_id=event_id)
    except ValidationError as e:
        raise ToolError(format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(
            f"/api/planner/event/{validated.calendar_id}/{validated.event_id}/pin",
            {},
        )
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        # fmt: off
        raise ToolError(
            f"Event {validated.event_id} not found in calendar "
            f"{validated.calendar_id}"
        )
        # fmt: on
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error pinning event {validated.event_id}: {e}")


async def unpin_event(calendar_id: int, event_id: str) -> dict:
    """Unpin an event to allow it to be rescheduled by the AI.

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to unpin

    Returns:
        Planner action result with updated event state.
    """
    # Validate input using Pydantic model
    try:
        validated = CalendarEventId(calendar_id=calendar_id, event_id=event_id)
    except ValidationError as e:
        raise ToolError(format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.post(
            f"/api/planner/event/{validated.calendar_id}/{validated.event_id}/unpin",
            {},
        )
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        # fmt: off
        raise ToolError(
            f"Event {validated.event_id} not found in calendar "
            f"{validated.calendar_id}"
        )
        # fmt: on
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error unpinning event {validated.event_id}: {e}")


async def set_event_rsvp(
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
    # Validate input using Pydantic model
    try:
        validated = EventRsvp(
            calendar_id=calendar_id,
            event_id=event_id,
            rsvp_status=rsvp_status,  # type: ignore[arg-type]
        )
    except ValidationError as e:
        raise ToolError(format_validation_errors(e))

    try:
        client = _get_client()
        result = await client.put(
            f"/api/planner/event/rsvp/{validated.calendar_id}/{validated.event_id}",
            {
                "responseStatus": validated.rsvp_status.value,
                "sendUpdates": send_updates,
            },
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
    # Validate input using Pydantic model
    try:
        validated = EventMove(
            event_id=event_id,
            start_time=start_time,
            end_time=end_time,
        )
    except ValidationError as e:
        raise ToolError(format_validation_errors(e))

    try:
        client = _get_client()
        # v1 API: uses query params instead of body
        result = await client.post(
            f"/api/planner/event/move/{validated.event_id}",
            {},  # Empty body
            params={"start": validated.start_time, "end": validated.end_time},
        )
        invalidate_cache("list_events")
        invalidate_cache("list_personal_events")
        return result
    except NotFoundError:
        raise ToolError(f"Event {event_id} not found")
    except RateLimitError as e:
        raise ToolError(str(e))
    except ReclaimError as e:
        raise ToolError(f"Error moving event {event_id}: {e}")
