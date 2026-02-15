"""Tests for Pydantic models."""

import pytest

from reclaim_mcp.models import FocusSettingsUpdate, Task, TaskCreate, TaskStatus


class TestTaskModel:
    """Tests for Task model."""

    def test_task_from_api_response(self, mock_task_response: dict) -> None:
        """Test Task model parses API response correctly."""
        task = Task(**mock_task_response)

        assert task.id == 12345
        assert task.title == "Test Task"
        assert task.status == TaskStatus.NEW
        assert task.time_chunks_required == 4
        assert task.time_chunks_spent == 0
        assert task.min_chunk_size == 15
        assert task.max_chunk_size == 60

    def test_task_with_null_fields(self) -> None:
        """Test Task model handles null optional fields."""
        data = {
            "id": 1,
            "title": "Simple Task",
            "status": "NEW",
            "timeChunksRequired": 2,
            "minChunkSize": 15,
            "maxChunkSize": 30,
        }
        task = Task(**data)

        assert task.due is None
        assert task.snooze_until is None
        assert task.time_chunks_spent == 0


class TestTaskCreateModel:
    """Tests for TaskCreate model."""

    def test_task_create_minimal(self) -> None:
        """Test TaskCreate with minimal required fields."""
        task = TaskCreate(title="New Task", duration_minutes=60)

        assert task.title == "New Task"
        assert task.duration_minutes == 60
        assert task.min_chunk_size_minutes == 15  # default

    def test_task_create_serialization(self) -> None:
        """Test TaskCreate serializes with correct field names."""
        task = TaskCreate(title="New Task", duration_minutes=60, min_chunk_size_minutes=30)

        data = task.model_dump(exclude_none=True)

        assert data["title"] == "New Task"
        assert data["duration_minutes"] == 60
        assert data["min_chunk_size_minutes"] == 30


class TestFocusSettingsUpdate:
    """Tests for FocusSettingsUpdate model validation."""

    def test_focus_settings_update_min_exceeds_ideal(self) -> None:
        """Test that min > ideal raises ValueError."""
        with pytest.raises(ValueError, match="min_duration_mins cannot exceed ideal_duration_mins"):
            FocusSettingsUpdate(min_duration_mins=60, ideal_duration_mins=30)

    def test_focus_settings_update_ideal_exceeds_max(self) -> None:
        """Test that ideal > max raises ValueError."""
        with pytest.raises(ValueError, match="ideal_duration_mins cannot exceed max_duration_mins"):
            FocusSettingsUpdate(ideal_duration_mins=60, max_duration_mins=30)

    def test_focus_settings_update_valid_ordering(self) -> None:
        """Test that valid min < ideal < max passes validation."""
        settings = FocusSettingsUpdate(min_duration_mins=15, ideal_duration_mins=30, max_duration_mins=60)
        assert settings.min_duration_mins == 15
        assert settings.ideal_duration_mins == 30
        assert settings.max_duration_mins == 60
