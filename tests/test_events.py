"""Tests for calendar and event tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from reclaim_mcp.tools import events
from reclaim_mcp.tools.events import _extract_date


class TestExtractDate:
    """Tests for _extract_date helper function."""

    def test_extract_date_from_datetime(self) -> None:
        """Test extracting date from full datetime string."""
        assert _extract_date("2026-01-02T00:00:00Z") == "2026-01-02"
        assert _extract_date("2026-01-02T23:59:59Z") == "2026-01-02"

    def test_extract_date_from_date_only(self) -> None:
        """Test extracting date from date-only string."""
        assert _extract_date("2026-01-02") == "2026-01-02"


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock ReclaimClient."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client


class TestListEvents:
    """Tests for list_events function."""

    @pytest.mark.asyncio
    async def test_list_events_required_params(
        self, mock_client: MagicMock, mock_events_list_response: list[dict]
    ) -> None:
        """Test list_events with required start and end params."""
        mock_client.get.return_value = mock_events_list_response

        with patch.object(events, "_get_client", return_value=mock_client):
            result = await events.list_events(
                start="2026-01-02T00:00:00Z",
                end="2026-01-02T23:59:59Z",
            )

        assert result == mock_events_list_response
        # API uses date format (YYYY-MM-DD), not datetime
        mock_client.get.assert_called_once_with(
            "/api/events",
            params={
                "start": "2026-01-02",
                "end": "2026-01-02",
                "thin": True,
            },
        )

    @pytest.mark.asyncio
    async def test_list_events_with_calendar_ids(
        self, mock_client: MagicMock, mock_events_list_response: list[dict]
    ) -> None:
        """Test list_events with calendar_ids filter."""
        mock_client.get.return_value = mock_events_list_response

        with patch.object(events, "_get_client", return_value=mock_client):
            result = await events.list_events(
                start="2026-01-02T00:00:00Z",
                end="2026-01-02T23:59:59Z",
                calendar_ids=[1, 2, 3],
            )

        assert result == mock_events_list_response
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["calendarIds"] == "1,2,3"

    @pytest.mark.asyncio
    async def test_list_events_with_event_type(self, mock_client: MagicMock) -> None:
        """Test list_events with event type filter."""
        mock_client.get.return_value = []

        with patch.object(events, "_get_client", return_value=mock_client):
            result = await events.list_events(
                start="2026-01-02T00:00:00Z",
                end="2026-01-02T23:59:59Z",
                event_type="EXTERNAL",
                thin=False,
            )

        assert result == []
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["type"] == "EXTERNAL"
        assert call_args[1]["params"]["thin"] is False


class TestListPersonalEvents:
    """Tests for list_personal_events function."""

    @pytest.mark.asyncio
    async def test_list_personal_events_default(
        self, mock_client: MagicMock, mock_events_list_response: list[dict]
    ) -> None:
        """Test list_personal_events with default parameters.

        When no dates are provided, defaults to current week (today + 7 days).
        """
        mock_client.get.return_value = mock_events_list_response

        with patch.object(events, "_get_client", return_value=mock_client):
            result = await events.list_personal_events()

        assert result == mock_events_list_response
        # Verify call was made with dates (defaults to current week)
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/api/events/personal"
        params = call_args[1]["params"]
        assert params["limit"] == 50
        assert "start" in params  # Now defaults to today
        assert "end" in params  # Now defaults to today + 7 days

    @pytest.mark.asyncio
    async def test_list_personal_events_with_date_range(self, mock_client: MagicMock) -> None:
        """Test list_personal_events with date range and custom limit."""
        mock_client.get.return_value = []

        with patch.object(events, "_get_client", return_value=mock_client):
            result = await events.list_personal_events(
                start="2026-01-02T00:00:00Z",
                end="2026-01-08T23:59:59Z",
                limit=100,
            )

        assert result == []
        # Dates are extracted from datetime strings (YYYY-MM-DD format required by API)
        mock_client.get.assert_called_once_with(
            "/api/events/personal",
            params={
                "start": "2026-01-02",
                "end": "2026-01-08",
                "limit": 100,
            },
        )


class TestGetEvent:
    """Tests for get_event function."""

    @pytest.mark.asyncio
    async def test_get_event(self, mock_client: MagicMock, mock_event_response: dict) -> None:
        """Test get_event returns single event."""
        mock_client.get.return_value = mock_event_response

        with patch.object(events, "_get_client", return_value=mock_client):
            result = await events.get_event(calendar_id=1, event_id="abc123xyz")

        assert result == mock_event_response
        mock_client.get.assert_called_once_with(
            "/api/events/1/abc123xyz",
            params={"thin": False},
        )

    @pytest.mark.asyncio
    async def test_get_event_with_thin(self, mock_client: MagicMock) -> None:
        """Test get_event with thin parameter."""
        mock_client.get.return_value = {"eventId": "abc", "title": "Test"}

        with patch.object(events, "_get_client", return_value=mock_client):
            result = await events.get_event(
                calendar_id=1,
                event_id="abc123xyz",
                thin=True,
            )

        assert result["eventId"] == "abc"
        mock_client.get.assert_called_once_with(
            "/api/events/1/abc123xyz",
            params={"thin": True},
        )
