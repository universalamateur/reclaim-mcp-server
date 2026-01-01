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
