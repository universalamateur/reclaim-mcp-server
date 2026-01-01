"""Tests for smart habit tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from reclaim_mcp.tools import habits


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock ReclaimClient."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.patch = AsyncMock()
    client.delete = AsyncMock()
    return client


class TestListHabits:
    """Tests for list_habits function."""

    @pytest.mark.asyncio
    async def test_list_habits(self, mock_client: MagicMock, mock_habits_list_response: list[dict]) -> None:
        """Test list_habits returns all habits."""
        mock_client.get.return_value = mock_habits_list_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.list_habits()

        assert result == mock_habits_list_response
        mock_client.get.assert_called_once_with("/api/smart-habits")

    @pytest.mark.asyncio
    async def test_list_habits_empty(self, mock_client: MagicMock) -> None:
        """Test list_habits returns empty list when no habits exist."""
        mock_client.get.return_value = []

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.list_habits()

        assert result == []


class TestGetHabit:
    """Tests for get_habit function."""

    @pytest.mark.asyncio
    async def test_get_habit(self, mock_client: MagicMock, mock_habit_response: dict) -> None:
        """Test get_habit returns a single habit."""
        mock_client.get.return_value = mock_habit_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.get_habit(lineage_id=12345)

        assert result == mock_habit_response
        mock_client.get.assert_called_once_with("/api/smart-habits/12345")


class TestCreateHabit:
    """Tests for create_habit function."""

    @pytest.mark.asyncio
    async def test_create_habit_minimal(self, mock_client: MagicMock, mock_habit_response: dict) -> None:
        """Test create_habit with minimal required params."""
        mock_client.post.return_value = mock_habit_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.create_habit(
                title="Morning Meditation",
                ideal_time="07:00",
                duration_min_mins=15,
            )

        assert result == mock_habit_response
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/api/smart-habits"
        payload = call_args[1]["data"]
        assert payload["title"] == "Morning Meditation"
        assert payload["idealTime"] == "07:00:00"  # Normalized to HH:MM:SS
        assert payload["durationMinMins"] == 15
        assert payload["durationMaxMins"] == 15  # Defaults to min
        assert payload["enabled"] is True
        assert payload["organizer"]["timePolicyType"] == "WORK"  # Default for SOLO_WORK
        assert payload["eventType"] == "SOLO_WORK"
        assert payload["defenseAggression"] == "DEFAULT"
        assert payload["recurrence"]["frequency"] == "WEEKLY"

    @pytest.mark.asyncio
    async def test_create_habit_with_options(self, mock_client: MagicMock, mock_habit_response: dict) -> None:
        """Test create_habit with all optional params."""
        mock_client.post.return_value = mock_habit_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.create_habit(
                title="Weekly Review",
                ideal_time="16:00",
                duration_min_mins=60,
                frequency="WEEKLY",
                ideal_days=["FRIDAY"],
                event_type="FOCUS",
                defense_aggression="HIGH",
                duration_max_mins=90,
                description="End of week review",
            )

        assert result == mock_habit_response
        payload = mock_client.post.call_args[1]["data"]
        assert payload["title"] == "Weekly Review"
        assert payload["durationMinMins"] == 60
        assert payload["durationMaxMins"] == 90
        assert payload["eventType"] == "FOCUS"
        assert payload["defenseAggression"] == "HIGH"
        assert payload["organizer"]["timePolicyType"] == "WORK"  # FOCUS defaults to WORK
        assert payload["description"] == "End of week review"
        assert payload["recurrence"]["frequency"] == "WEEKLY"
        assert payload["recurrence"]["idealDays"] == ["FRIDAY"]


class TestUpdateHabit:
    """Tests for update_habit function."""

    @pytest.mark.asyncio
    async def test_update_habit_title(self, mock_client: MagicMock, mock_habit_response: dict) -> None:
        """Test update_habit changes title."""
        mock_client.patch.return_value = mock_habit_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.update_habit(
                lineage_id=12345,
                title="Updated Meditation",
            )

        assert result == mock_habit_response
        mock_client.patch.assert_called_once_with(
            "/api/smart-habits/12345",
            data={"title": "Updated Meditation"},
        )

    @pytest.mark.asyncio
    async def test_update_habit_multiple_fields(self, mock_client: MagicMock, mock_habit_response: dict) -> None:
        """Test update_habit with multiple fields."""
        mock_client.patch.return_value = mock_habit_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.update_habit(
                lineage_id=12345,
                title="Updated Habit",
                ideal_time="08:00",
                duration_min_mins=30,
                enabled=False,
            )

        assert result == mock_habit_response
        payload = mock_client.patch.call_args[1]["data"]
        assert payload["title"] == "Updated Habit"
        assert payload["idealTime"] == "08:00:00"  # Normalized to HH:MM:SS
        assert payload["durationMinMins"] == 30
        assert payload["enabled"] is False

    @pytest.mark.asyncio
    async def test_update_habit_recurrence(self, mock_client: MagicMock, mock_habit_response: dict) -> None:
        """Test update_habit with recurrence changes."""
        mock_client.patch.return_value = mock_habit_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.update_habit(
                lineage_id=12345,
                frequency="DAILY",
            )

        assert result == mock_habit_response
        payload = mock_client.patch.call_args[1]["data"]
        assert payload["recurrence"]["frequency"] == "DAILY"


class TestDeleteHabit:
    """Tests for delete_habit function."""

    @pytest.mark.asyncio
    async def test_delete_habit(self, mock_client: MagicMock) -> None:
        """Test delete_habit returns True on success."""
        mock_client.delete.return_value = None

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.delete_habit(lineage_id=12345)

        assert result is True
        mock_client.delete.assert_called_once_with("/api/smart-habits/12345")


class TestMarkHabitDone:
    """Tests for mark_habit_done function."""

    @pytest.mark.asyncio
    async def test_mark_habit_done(self, mock_client: MagicMock, mock_habit_action_response: dict) -> None:
        """Test mark_habit_done calls correct endpoint."""
        mock_client.post.return_value = mock_habit_action_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.mark_habit_done(event_id="evt_abc123")

        assert result == mock_habit_action_response
        mock_client.post.assert_called_once_with("/api/smart-habits/planner/evt_abc123/done", data={})


class TestSkipHabit:
    """Tests for skip_habit function."""

    @pytest.mark.asyncio
    async def test_skip_habit(self, mock_client: MagicMock, mock_habit_action_response: dict) -> None:
        """Test skip_habit calls correct endpoint."""
        mock_client.post.return_value = mock_habit_action_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.skip_habit(event_id="evt_abc123")

        assert result == mock_habit_action_response
        mock_client.post.assert_called_once_with("/api/smart-habits/planner/evt_abc123/skip", data={})


class TestLockHabitInstance:
    """Tests for lock_habit_instance function."""

    @pytest.mark.asyncio
    async def test_lock_habit_instance(self, mock_client: MagicMock, mock_habit_action_response: dict) -> None:
        """Test lock_habit_instance calls correct endpoint."""
        mock_client.post.return_value = mock_habit_action_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.lock_habit_instance(event_id="evt_abc123")

        assert result == mock_habit_action_response
        mock_client.post.assert_called_once_with("/api/smart-habits/planner/evt_abc123/lock", data={})


class TestUnlockHabitInstance:
    """Tests for unlock_habit_instance function."""

    @pytest.mark.asyncio
    async def test_unlock_habit_instance(self, mock_client: MagicMock, mock_habit_action_response: dict) -> None:
        """Test unlock_habit_instance calls correct endpoint."""
        mock_client.post.return_value = mock_habit_action_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.unlock_habit_instance(event_id="evt_abc123")

        assert result == mock_habit_action_response
        mock_client.post.assert_called_once_with("/api/smart-habits/planner/evt_abc123/unlock", data={})


class TestStartHabit:
    """Tests for start_habit function."""

    @pytest.mark.asyncio
    async def test_start_habit(self, mock_client: MagicMock, mock_habit_action_response: dict) -> None:
        """Test start_habit calls correct endpoint."""
        mock_client.post.return_value = mock_habit_action_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.start_habit(lineage_id=12345)

        assert result == mock_habit_action_response
        mock_client.post.assert_called_once_with("/api/smart-habits/planner/12345/start", data={})


class TestStopHabit:
    """Tests for stop_habit function."""

    @pytest.mark.asyncio
    async def test_stop_habit(self, mock_client: MagicMock, mock_habit_action_response: dict) -> None:
        """Test stop_habit calls correct endpoint."""
        mock_client.post.return_value = mock_habit_action_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.stop_habit(lineage_id=12345)

        assert result == mock_habit_action_response
        mock_client.post.assert_called_once_with("/api/smart-habits/planner/12345/stop", data={})


class TestEnableHabit:
    """Tests for enable_habit function."""

    @pytest.mark.asyncio
    async def test_enable_habit(self, mock_client: MagicMock) -> None:
        """Test enable_habit calls correct endpoint."""
        mock_client.post.return_value = {}

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.enable_habit(lineage_id=12345)

        assert result == {}
        mock_client.post.assert_called_once_with("/api/smart-habits/12345/enable", data={})


class TestDisableHabit:
    """Tests for disable_habit function."""

    @pytest.mark.asyncio
    async def test_disable_habit(self, mock_client: MagicMock) -> None:
        """Test disable_habit calls correct endpoint."""
        mock_client.delete.return_value = None

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.disable_habit(lineage_id=12345)

        assert result is True
        mock_client.delete.assert_called_once_with("/api/smart-habits/12345/disable")


class TestConvertEventToHabit:
    """Tests for convert_event_to_habit function."""

    @pytest.mark.asyncio
    async def test_convert_event_to_habit_minimal(self, mock_client: MagicMock, mock_habit_response: dict) -> None:
        """Test convert_event_to_habit with minimal required params."""
        mock_client.post.return_value = mock_habit_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.convert_event_to_habit(
                calendar_id=1001,
                event_id="evt_xyz789",
                title="Weekly Meeting",
                ideal_time="09:00",
                duration_min_mins=30,
            )

        assert result == mock_habit_response
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/api/smart-habits/convert/1001/evt_xyz789"
        payload = call_args[1]["data"]
        assert payload["title"] == "Weekly Meeting"
        assert payload["idealTime"] == "09:00:00"  # Normalized to HH:MM:SS
        assert payload["durationMinMins"] == 30
        assert payload["durationMaxMins"] == 30  # Defaults to min
        assert payload["enabled"] is True
        assert payload["organizer"]["timePolicyType"] == "WORK"
        assert payload["eventType"] == "SOLO_WORK"
        assert payload["defenseAggression"] == "DEFAULT"
        assert payload["recurrence"]["frequency"] == "WEEKLY"

    @pytest.mark.asyncio
    async def test_convert_event_to_habit_with_options(self, mock_client: MagicMock, mock_habit_response: dict) -> None:
        """Test convert_event_to_habit with all optional params."""
        mock_client.post.return_value = mock_habit_response

        with patch.object(habits, "_get_client", return_value=mock_client):
            result = await habits.convert_event_to_habit(
                calendar_id=1001,
                event_id="evt_xyz789",
                title="Team Standup",
                ideal_time="10:00",
                duration_min_mins=15,
                frequency="DAILY",
                ideal_days=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
                event_type="TEAM_MEETING",
                defense_aggression="HIGH",
                duration_max_mins=30,
                description="Daily team standup",
                time_policy_type="MEETING",
            )

        assert result == mock_habit_response
        payload = mock_client.post.call_args[1]["data"]
        assert payload["title"] == "Team Standup"
        assert payload["durationMinMins"] == 15
        assert payload["durationMaxMins"] == 30
        assert payload["eventType"] == "TEAM_MEETING"
        assert payload["defenseAggression"] == "HIGH"
        assert payload["organizer"]["timePolicyType"] == "MEETING"
        assert payload["description"] == "Daily team standup"
        assert payload["recurrence"]["frequency"] == "DAILY"
        assert payload["recurrence"]["idealDays"] == ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
