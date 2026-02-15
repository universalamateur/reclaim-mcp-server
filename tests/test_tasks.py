"""Tests for task management tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from reclaim_mcp.tools import tasks


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock ReclaimClient."""
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.patch = AsyncMock()
    client.delete = AsyncMock()
    return client


class TestListTasks:
    """Tests for list_tasks function."""

    @pytest.mark.asyncio
    async def test_list_tasks_default_params(
        self, mock_client: MagicMock, mock_tasks_list_response: list[dict]
    ) -> None:
        """Test list_tasks with default parameters."""
        mock_client.get.return_value = mock_tasks_list_response

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.list_tasks()

        assert result == mock_tasks_list_response
        mock_client.get.assert_called_once_with(
            "/api/tasks", params={"status": "NEW,SCHEDULED,IN_PROGRESS", "limit": 50}
        )

    @pytest.mark.asyncio
    async def test_list_tasks_custom_params(self, mock_client: MagicMock) -> None:
        """Test list_tasks with custom status and limit."""
        mock_client.get.return_value = []

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.list_tasks(status="COMPLETE", limit=10)

        assert result == []
        mock_client.get.assert_called_once_with("/api/tasks", params={"status": "COMPLETE", "limit": 10})


class TestListCompletedTasks:
    """Tests for list_completed_tasks function."""

    @pytest.mark.asyncio
    async def test_list_completed_tasks_default(self, mock_client: MagicMock) -> None:
        """Test list_completed_tasks returns completed and archived tasks."""
        completed_tasks = [{"id": 1, "status": "COMPLETE"}, {"id": 2, "status": "ARCHIVED"}]
        mock_client.get.return_value = completed_tasks

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.list_completed_tasks()

        assert result == completed_tasks
        mock_client.get.assert_called_once_with("/api/tasks", params={"status": "COMPLETE,ARCHIVED", "limit": 50})

    @pytest.mark.asyncio
    async def test_list_completed_tasks_custom_limit(self, mock_client: MagicMock) -> None:
        """Test list_completed_tasks with custom limit."""
        mock_client.get.return_value = []

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.list_completed_tasks(limit=100)

        assert result == []
        mock_client.get.assert_called_once_with("/api/tasks", params={"status": "COMPLETE,ARCHIVED", "limit": 100})


class TestGetTask:
    """Tests for get_task function."""

    @pytest.mark.asyncio
    async def test_get_task(self, mock_client: MagicMock, mock_task_response: dict) -> None:
        """Test get_task returns single task."""
        mock_client.get.return_value = mock_task_response

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.get_task(task_id=12345)

        assert result == mock_task_response
        mock_client.get.assert_called_once_with("/api/tasks/12345")


class TestCreateTask:
    """Tests for create_task function."""

    @pytest.mark.asyncio
    async def test_create_task_minimal(self, mock_client: MagicMock, mock_task_response: dict) -> None:
        """Test create_task with minimal required parameters."""
        mock_client.post.return_value = mock_task_response

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.create_task(title="Test Task", duration_minutes=60)

        assert result == mock_task_response
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "/api/tasks"
        payload = call_args[0][1]
        assert payload["title"] == "Test Task"
        assert payload["timeChunksRequired"] == 4  # 60 / 15 = 4
        assert payload["minChunkSize"] == 15
        assert payload["maxChunkSize"] == 60
        assert payload["eventCategory"] == "WORK"
        assert payload["priority"] == "P2"
        assert "deadline" not in payload
        assert "snoozeUntil" not in payload

    @pytest.mark.asyncio
    async def test_create_task_with_all_options(self, mock_client: MagicMock, mock_task_response: dict) -> None:
        """Test create_task with all optional parameters."""
        mock_client.post.return_value = mock_task_response

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.create_task(
                title="Full Task",
                duration_minutes=120,
                due_date="2026-01-15",
                min_chunk_size_minutes=30,
                max_chunk_size_minutes=60,
                snooze_until="2026-01-10T09:00:00Z",
                priority="P1",
            )

        assert result == mock_task_response
        call_args = mock_client.post.call_args
        payload = call_args[0][1]
        assert payload["title"] == "Full Task"
        assert payload["timeChunksRequired"] == 8  # 120 / 15 = 8
        assert payload["minChunkSize"] == 30
        assert payload["maxChunkSize"] == 60
        assert payload["priority"] == "P1"
        assert payload["deadline"] == "2026-01-15"
        assert payload["snoozeUntil"] == "2026-01-10T09:00:00Z"

    @pytest.mark.asyncio
    async def test_create_task_small_duration(self, mock_client: MagicMock) -> None:
        """Test create_task with duration less than 15 minutes rounds up to 1 chunk."""
        mock_client.post.return_value = {"id": 1}

        with patch.object(tasks, "_get_client", return_value=mock_client):
            await tasks.create_task(title="Quick Task", duration_minutes=5)

        call_args = mock_client.post.call_args
        payload = call_args[0][1]
        assert payload["timeChunksRequired"] == 1  # Minimum 1 chunk


class TestUpdateTask:
    """Tests for update_task function."""

    @pytest.mark.asyncio
    async def test_update_task_title(self, mock_client: MagicMock, mock_task_response: dict) -> None:
        """Test update_task with title change."""
        mock_client.patch.return_value = mock_task_response

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.update_task(task_id=12345, title="Updated Title")

        assert result == mock_task_response
        mock_client.patch.assert_called_once_with("/api/tasks/12345", {"title": "Updated Title"})

    @pytest.mark.asyncio
    async def test_update_task_duration(self, mock_client: MagicMock) -> None:
        """Test update_task with duration change converts to time chunks."""
        mock_client.patch.return_value = {"id": 12345}

        with patch.object(tasks, "_get_client", return_value=mock_client):
            await tasks.update_task(task_id=12345, duration_minutes=90)

        mock_client.patch.assert_called_once_with("/api/tasks/12345", {"timeChunksRequired": 6})  # 90 / 15 = 6

    @pytest.mark.asyncio
    async def test_update_task_multiple_fields(self, mock_client: MagicMock) -> None:
        """Test update_task with multiple field updates."""
        mock_client.patch.return_value = {"id": 12345}

        with patch.object(tasks, "_get_client", return_value=mock_client):
            await tasks.update_task(
                task_id=12345,
                title="New Title",
                status="IN_PROGRESS",
                due_date="2026-02-01",
            )

        mock_client.patch.assert_called_once_with(
            "/api/tasks/12345",
            {
                "title": "New Title",
                "status": "IN_PROGRESS",
                "due": "2026-02-01",
            },
        )

    @pytest.mark.asyncio
    async def test_update_task_small_duration(self, mock_client: MagicMock) -> None:
        """Test update_task with duration < 15 min gets minimum 1 time chunk."""
        mock_client.patch.return_value = {"id": 12345}

        with patch.object(tasks, "_get_client", return_value=mock_client):
            await tasks.update_task(task_id=12345, duration_minutes=5)

        mock_client.patch.assert_called_once_with("/api/tasks/12345", {"timeChunksRequired": 1})

    @pytest.mark.asyncio
    async def test_update_task_no_changes(self, mock_client: MagicMock) -> None:
        """Test update_task with no changes sends empty payload."""
        mock_client.patch.return_value = {"id": 12345}

        with patch.object(tasks, "_get_client", return_value=mock_client):
            await tasks.update_task(task_id=12345)

        mock_client.patch.assert_called_once_with("/api/tasks/12345", {})


class TestMarkTaskComplete:
    """Tests for mark_task_complete function."""

    @pytest.mark.asyncio
    async def test_mark_task_complete(self, mock_client: MagicMock, mock_task_response: dict) -> None:
        """Test mark_task_complete calls correct endpoint."""
        completed_task = {**mock_task_response, "status": "COMPLETE"}
        mock_client.post.return_value = completed_task

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.mark_task_complete(task_id=12345)

        assert result["status"] == "COMPLETE"
        mock_client.post.assert_called_once_with("/api/planner/done/task/12345", {})


class TestDeleteTask:
    """Tests for delete_task function."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self, mock_client: MagicMock) -> None:
        """Test delete_task returns True on success."""
        mock_client.delete.return_value = True

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.delete_task(task_id=12345)

        assert result is True
        mock_client.delete.assert_called_once_with("/api/tasks/12345")

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, mock_client: MagicMock) -> None:
        """Test delete_task returns False when task not found."""
        mock_client.delete.return_value = False

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.delete_task(task_id=99999)

        assert result is False


class TestAddTimeToTask:
    """Tests for add_time_to_task function."""

    @pytest.mark.asyncio
    async def test_add_time_to_task(self, mock_client: MagicMock) -> None:
        """Test add_time_to_task uses planner log-work endpoint."""
        mock_client.post.return_value = {"status": "OK"}

        with patch.object(tasks, "_get_client", return_value=mock_client):
            result = await tasks.add_time_to_task(task_id=12345, minutes=30)

        assert result == {"status": "OK"}
        mock_client.post.assert_called_once_with(
            "/api/planner/log-work/task/12345",
            {},
            params={"minutes": 30},
        )

    @pytest.mark.asyncio
    async def test_add_time_to_task_with_notes(self, mock_client: MagicMock) -> None:
        """Test add_time_to_task with notes updates task separately."""
        mock_client.post.return_value = {"status": "OK"}
        mock_client.patch.return_value = {"id": 12345}

        with patch.object(tasks, "_get_client", return_value=mock_client):
            await tasks.add_time_to_task(task_id=12345, minutes=45, notes="Completed research phase")

        mock_client.post.assert_called_once_with(
            "/api/planner/log-work/task/12345",
            {},
            params={"minutes": 45},
        )
        mock_client.patch.assert_called_once_with("/api/tasks/12345", {"notes": "Completed research phase"})

    @pytest.mark.asyncio
    async def test_add_time_to_task_small_duration(self, mock_client: MagicMock) -> None:
        """Test add_time_to_task passes minutes directly to API."""
        mock_client.post.return_value = {"status": "OK"}

        with patch.object(tasks, "_get_client", return_value=mock_client):
            await tasks.add_time_to_task(task_id=12345, minutes=5)

        # API handles the conversion, we just pass minutes as-is
        mock_client.post.assert_called_once_with(
            "/api/planner/log-work/task/12345",
            {},
            params={"minutes": 5},
        )
