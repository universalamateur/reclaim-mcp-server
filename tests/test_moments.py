"""Tests for moment/context tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from reclaim_mcp.tools import moments


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock ReclaimClient."""
    client = MagicMock()
    client.get = AsyncMock()
    return client


class TestGetCurrentMoment:
    """Tests for get_current_moment function."""

    @pytest.mark.asyncio
    async def test_get_current_moment(self, mock_client: MagicMock) -> None:
        """Test get_current_moment returns current activity."""
        mock_response = {
            "event": {"title": "Focus Time", "eventStart": "2026-02-22T10:00:00Z"},
            "status": "BUSY",
        }
        mock_client.get.return_value = mock_response

        with patch.object(moments, "_get_client", return_value=mock_client):
            result = await moments.get_current_moment()

        assert result == mock_response
        mock_client.get.assert_called_once_with("/api/moment")


class TestGetNextMoment:
    """Tests for get_next_moment function."""

    @pytest.mark.asyncio
    async def test_get_next_moment(self, mock_client: MagicMock) -> None:
        """Test get_next_moment returns upcoming activity."""
        mock_response = {
            "event": {"title": "Team Standup", "eventStart": "2026-02-22T10:30:00Z"},
            "status": "UPCOMING",
        }
        mock_client.get.return_value = mock_response

        with patch.object(moments, "_get_client", return_value=mock_client):
            result = await moments.get_next_moment()

        assert result == mock_response
        mock_client.get.assert_called_once_with("/api/moment/next")
