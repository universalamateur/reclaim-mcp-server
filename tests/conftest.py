"""Pytest fixtures for Reclaim MCP server tests."""

import pytest

from reclaim_mcp.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Create test settings with a dummy API key."""
    return Settings(api_key="test_api_key_12345")


@pytest.fixture
def mock_task_response() -> dict:
    """Sample task response from Reclaim.ai API."""
    return {
        "id": 12345,
        "title": "Test Task",
        "status": "NEW",
        "timeChunksRequired": 4,
        "timeChunksSpent": 0,
        "minChunkSize": 15,
        "maxChunkSize": 60,
        "due": "2026-01-15T17:00:00Z",
        "snoozeUntil": None,
        "created": "2026-01-01T10:00:00Z",
        "updated": "2026-01-01T10:00:00Z",
    }


@pytest.fixture
def mock_tasks_list_response(mock_task_response: dict) -> list[dict]:
    """Sample tasks list response from Reclaim.ai API."""
    return [
        mock_task_response,
        {
            "id": 12346,
            "title": "Another Task",
            "status": "SCHEDULED",
            "timeChunksRequired": 2,
            "timeChunksSpent": 1,
            "minChunkSize": 30,
            "maxChunkSize": 30,
            "due": None,
            "snoozeUntil": None,
            "created": "2026-01-01T11:00:00Z",
            "updated": "2026-01-01T12:00:00Z",
        },
    ]


# Event fixtures (Phase 5)


@pytest.fixture
def mock_event_response() -> dict:
    """Sample event response from Reclaim.ai API."""
    return {
        "eventId": "abc123xyz",
        "calendarId": 1,
        "title": "Team Standup",
        "eventStart": "2026-01-02T10:00:00Z",
        "eventEnd": "2026-01-02T10:30:00Z",
        "location": "Zoom",
        "description": "Daily team standup meeting",
        "organizer": "team@example.com",
        "priority": "P2",
        "type": "EXTERNAL",
        "meetingType": "MEETING",
        "rsvpStatus": "ACCEPTED",
        "reclaimManaged": False,
    }


@pytest.fixture
def mock_events_list_response(mock_event_response: dict) -> list[dict]:
    """Sample events list response from Reclaim.ai API."""
    return [
        mock_event_response,
        {
            "eventId": "def456uvw",
            "calendarId": 1,
            "title": "Focus Time",
            "eventStart": "2026-01-02T14:00:00Z",
            "eventEnd": "2026-01-02T16:00:00Z",
            "location": None,
            "description": "Auto-scheduled focus time",
            "organizer": None,
            "priority": "P3",
            "type": "RECLAIM_MANAGED",
            "meetingType": None,
            "rsvpStatus": None,
            "reclaimManaged": True,
        },
    ]
