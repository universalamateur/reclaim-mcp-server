"""Calendar and event tools for Reclaim.ai."""

from typing import Any, Optional

from reclaim_mcp.client import ReclaimClient
from reclaim_mcp.config import get_settings


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
        start: Start date in ISO format (e.g., '2026-01-02' or '2026-01-02T00:00:00Z')
        end: End date in ISO format (e.g., '2026-01-02' or '2026-01-02T23:59:59Z')
        calendar_ids: Optional list of calendar IDs to filter by
        event_type: Optional event type filter (EXTERNAL, RECLAIM_MANAGED, etc.)
        thin: If True, return minimal event data (default True)

    Returns:
        List of event objects with eventId, title, eventStart, eventEnd, etc.
    """
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
    client = _get_client()
    params: dict[str, Any] = {"limit": limit}
    if start:
        params["start"] = start
    if end:
        params["end"] = end

    events = await client.get("/api/events/personal", params=params)
    return events


async def get_event(
    calendar_id: int,
    event_id: str,
    thin: bool = False,
) -> dict:
    """Get a single event by calendar ID and event ID.

    Note: This endpoint works best with events from list_events (external calendar events).
    Events from list_personal_events (Reclaim-managed tasks/habits) may return 404 as they
    use a different event structure internally.

    Args:
        calendar_id: The calendar ID containing the event
        event_id: The event ID to retrieve
        thin: If True, return minimal event data (default False for full details)

    Returns:
        Event object with full details.
    """
    client = _get_client()
    params: dict[str, Any] = {"thin": thin}
    event = await client.get(f"/api/events/{calendar_id}/{event_id}", params=params)
    return event
