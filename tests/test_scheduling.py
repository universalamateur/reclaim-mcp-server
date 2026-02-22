"""Tests for scheduling tools (working hours and suggested times)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from reclaim_mcp.exceptions import ReclaimError
from reclaim_mcp.tools import scheduling


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock Reclaim client."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def mock_timeschemes_response() -> list[dict]:
    """Sample timeschemes API response."""
    return [
        {
            "id": "scheme-1",
            "title": "Work Hours",
            "policyType": "WORK",
            "status": "ACTIVE",
            "policy": {
                "dayHours": {
                    "MONDAY": {"startTime": "09:00:00", "endTime": "17:00:00", "intervals": []},
                    "TUESDAY": {"startTime": "09:00:00", "endTime": "17:00:00", "intervals": []},
                    "WEDNESDAY": {"startTime": "09:00:00", "endTime": "17:00:00", "intervals": []},
                    "THURSDAY": {"startTime": "09:00:00", "endTime": "17:00:00", "intervals": []},
                    "FRIDAY": {"startTime": "09:00:00", "endTime": "17:00:00", "intervals": []},
                }
            },
            "features": ["TASK", "FOCUS"],
        }
    ]


@pytest.fixture
def mock_suggested_times_response() -> dict:
    """Sample suggested-times API response."""
    return {
        "suggestedTimes": [
            {
                "start": "2026-02-23T10:00:00Z",
                "end": "2026-02-23T10:30:00Z",
                "availabilityInfo": {"score": 0.95},
            },
            {
                "start": "2026-02-23T14:00:00Z",
                "end": "2026-02-23T14:30:00Z",
                "availabilityInfo": {"score": 0.85},
            },
        ]
    }


class TestGetWorkingHours:
    """Tests for get_working_hours tool."""

    @pytest.mark.asyncio
    async def test_get_working_hours_success(
        self, mock_client: MagicMock, mock_timeschemes_response: list[dict]
    ) -> None:
        """Should return list of time schemes."""
        mock_client.get.return_value = mock_timeschemes_response

        with patch.object(scheduling, "_get_client", return_value=mock_client):
            result = await scheduling.get_working_hours()

        assert result == mock_timeschemes_response
        mock_client.get.assert_called_once_with("/api/timeschemes")

    @pytest.mark.asyncio
    async def test_get_working_hours_api_error(self, mock_client: MagicMock) -> None:
        """Should raise ToolError on API failure."""
        mock_client.get.side_effect = ReclaimError("Server error")

        with patch.object(scheduling, "_get_client", return_value=mock_client):
            with pytest.raises(ToolError, match="Error getting working hours"):
                await scheduling.get_working_hours()


class TestFindAvailableTimes:
    """Tests for find_available_times tool."""

    @pytest.mark.asyncio
    async def test_find_available_times_with_window(
        self, mock_client: MagicMock, mock_suggested_times_response: dict
    ) -> None:
        """Should POST with schedule window when dates provided."""
        mock_client.post.return_value = mock_suggested_times_response

        with patch.object(scheduling, "_get_client", return_value=mock_client):
            result = await scheduling.find_available_times(
                attendees=["alice@example.com", "bob@example.com"],
                duration_minutes=30,
                start_date="2026-02-23",
                end_date="2026-02-28",
                limit=5,
            )

        assert result == mock_suggested_times_response
        mock_client.post.assert_called_once_with(
            "/api/availability/suggested-times",
            data={
                "attendees": ["alice@example.com", "bob@example.com"],
                "durationMinutes": 30,
                "scheduleWindow": {"start": "2026-02-23", "end": "2026-02-28"},
                "limit": 5,
            },
        )

    @pytest.mark.asyncio
    async def test_find_available_times_without_window(
        self, mock_client: MagicMock, mock_suggested_times_response: dict
    ) -> None:
        """Should POST without schedule window when dates omitted."""
        mock_client.post.return_value = mock_suggested_times_response

        with patch.object(scheduling, "_get_client", return_value=mock_client):
            result = await scheduling.find_available_times(
                attendees=["alice@example.com"],
                duration_minutes=60,
            )

        assert result == mock_suggested_times_response
        mock_client.post.assert_called_once_with(
            "/api/availability/suggested-times",
            data={
                "attendees": ["alice@example.com"],
                "durationMinutes": 60,
            },
        )

    @pytest.mark.asyncio
    async def test_find_available_times_empty_attendees(self) -> None:
        """Should raise ToolError when attendees list is empty."""
        with pytest.raises(ToolError):
            await scheduling.find_available_times(
                attendees=[],
                duration_minutes=30,
            )

    @pytest.mark.asyncio
    async def test_find_available_times_partial_date_window(self) -> None:
        """Should raise ToolError when only one date is provided."""
        with pytest.raises(ToolError):
            await scheduling.find_available_times(
                attendees=["alice@example.com"],
                duration_minutes=30,
                start_date="2026-02-23",
            )

    @pytest.mark.asyncio
    async def test_find_available_times_invalid_duration(self) -> None:
        """Should raise ToolError for zero/negative duration."""
        with pytest.raises(ToolError):
            await scheduling.find_available_times(
                attendees=["alice@example.com"],
                duration_minutes=0,
            )

    @pytest.mark.asyncio
    async def test_find_available_times_api_error(self, mock_client: MagicMock) -> None:
        """Should raise ToolError on API failure."""
        mock_client.post.side_effect = ReclaimError("Server error")

        with patch.object(scheduling, "_get_client", return_value=mock_client):
            with pytest.raises(ToolError, match="Error finding available times"):
                await scheduling.find_available_times(
                    attendees=["alice@example.com"],
                    duration_minutes=30,
                )
