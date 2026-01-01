"""Tests for Pydantic models."""

from reclaim_mcp.models import Task, TaskCreate, TaskStatus


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
        task = TaskCreate(title="New Task", time_chunks_required=4)

        assert task.title == "New Task"
        assert task.time_chunks_required == 4
        assert task.min_chunk_size == 15  # default

    def test_task_create_serialization(self) -> None:
        """Test TaskCreate serializes with correct field names."""
        task = TaskCreate(title="New Task", time_chunks_required=4, min_chunk_size=30)

        # Use by_alias=True to get camelCase for API
        data = task.model_dump(by_alias=True, exclude_none=True)

        assert data["title"] == "New Task"
        assert data["timeChunksRequired"] == 4
        assert data["minChunkSize"] == 30
