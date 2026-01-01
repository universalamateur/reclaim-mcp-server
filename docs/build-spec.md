# Reclaim.ai MCP Server - Build Specification

## Project Overview

Build a personal MCP (Model Context Protocol) server using **FastMCP** (Python) to connect Reclaim.ai to Claude Desktop and Claude Code. This enables AI-assisted calendar management, task scheduling, and time blocking.

## Technical Stack

- **Framework**: FastMCP 2.0 (`pip install fastmcp`)
- **Language**: Python 3.10+
- **API Client**: `reclaim-sdk` (unofficial, `pip install reclaim-sdk`) OR direct HTTP requests
- **Transport**: stdio (for Claude Desktop) / SSE (for remote)

## Reclaim.ai API Reference

**Base URL**: `https://api.app.reclaim.ai`
**Auth**: Bearer token via `Authorization` header
**API Key**: Generate at https://app.reclaim.ai/settings/developer
**Swagger Spec**: https://api.app.reclaim.ai/swagger/reclaim-api-0.1.yml

## Required Tools to Implement

### 1. Task Management (Priority: High)

```python
@mcp.tool
def list_tasks(
    status: str = "NEW,SCHEDULED,IN_PROGRESS,COMPLETE",
    limit: int = 50
) -> list[dict]:
    """List all tasks from Reclaim.ai with optional status filter.
    
    Args:
        status: Comma-separated task statuses (NEW, SCHEDULED, IN_PROGRESS, COMPLETE)
        limit: Maximum number of tasks to return
    
    Returns:
        List of task objects with id, title, duration, due_date, status, etc.
    """
```

```python
@mcp.tool
def create_task(
    title: str,
    duration_minutes: int,
    due_date: str | None = None,
    min_chunk_size_minutes: int = 15,
    max_chunk_size_minutes: int | None = None,
    snooze_until: str | None = None,
    priority: str = "P2"
) -> dict:
    """Create a new task in Reclaim.ai for auto-scheduling.
    
    Args:
        title: Task title/description
        duration_minutes: Total time needed for the task
        due_date: ISO date string (YYYY-MM-DD) or None for no deadline
        min_chunk_size_minutes: Minimum time block size (default 15)
        max_chunk_size_minutes: Maximum time block size (None = duration)
        snooze_until: Don't schedule before this datetime
        priority: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)
    
    Returns:
        Created task object
    """
```

```python
@mcp.tool
def update_task(
    task_id: int,
    title: str | None = None,
    duration_minutes: int | None = None,
    due_date: str | None = None,
    status: str | None = None,
    priority: str | None = None
) -> dict:
    """Update an existing task in Reclaim.ai.
    
    Args:
        task_id: The task ID to update
        title: New title (optional)
        duration_minutes: New duration (optional)
        due_date: New due date (optional)
        status: New status - NEW, SCHEDULED, IN_PROGRESS, COMPLETE (optional)
        priority: New priority - P1, P2, P3, P4 (optional)
    
    Returns:
        Updated task object
    """
```

```python
@mcp.tool
def mark_task_complete(task_id: int) -> dict:
    """Mark a task as complete."""
```

```python
@mcp.tool
def delete_task(task_id: int) -> bool:
    """Delete a task from Reclaim.ai."""
```

```python
@mcp.tool
def add_time_to_task(task_id: int, minutes: int, notes: str | None = None) -> dict:
    """Log time spent on a task.
    
    Args:
        task_id: The task ID
        minutes: Minutes to add
        notes: Optional notes about the work done
    """
```

### 2. Habits Management (Priority: Medium)

```python
@mcp.tool
def list_habits() -> list[dict]:
    """List all daily habits configured in Reclaim.ai.
    
    Returns:
        List of habit objects with id, title, duration, schedule, etc.
    """
```

```python
@mcp.tool
def create_habit(
    title: str,
    duration_minutes: int,
    ideal_time: str = "MORNING",
    days_of_week: list[str] = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
) -> dict:
    """Create a recurring habit for auto-scheduling.
    
    Args:
        title: Habit name
        duration_minutes: Time needed per session
        ideal_time: MORNING, AFTERNOON, EVENING, or specific time like "09:00"
        days_of_week: Days to schedule the habit
    """
```

### 3. Calendar & Events (Priority: High)

```python
@mcp.tool
def list_events(
    start_date: str,
    end_date: str,
    calendar_ids: list[int] | None = None
) -> list[dict]:
    """List calendar events within a date range.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        calendar_ids: Specific calendar IDs or None for all connected
    
    Returns:
        List of event objects
    """
```

```python
@mcp.tool
def get_free_slots(
    start_date: str,
    end_date: str,
    duration_minutes: int = 30
) -> list[dict]:
    """Find available time slots in your calendar.
    
    Args:
        start_date: Start date to search
        end_date: End date to search
        duration_minutes: Minimum slot duration needed
    
    Returns:
        List of free time ranges
    """
```

### 4. Focus Time (Priority: Medium)

```python
@mcp.tool
def get_focus_time_settings() -> dict:
    """Get current focus time configuration."""
```

```python
@mcp.tool
def update_focus_time(
    enabled: bool | None = None,
    min_duration_minutes: int | None = None,
    ideal_duration_minutes: int | None = None
) -> dict:
    """Update focus time settings."""
```

### 5. Analytics (Priority: Low)

```python
@mcp.tool
def get_time_analytics(
    start_date: str,
    end_date: str
) -> dict:
    """Get time tracking analytics for a date range.
    
    Returns:
        Summary of time spent on tasks, meetings, focus time, etc.
    """
```

### 6. Scheduling Links (Priority: Low)

```python
@mcp.tool
def list_scheduling_links() -> list[dict]:
    """List all scheduling links."""
```

## Resources to Implement

```python
@mcp.resource("reclaim://tasks/active")
def active_tasks() -> str:
    """Resource providing current active tasks as context."""
    
@mcp.resource("reclaim://today")
def today_schedule() -> str:
    """Resource providing today's schedule overview."""

@mcp.resource("reclaim://week")
def week_schedule() -> str:
    """Resource providing this week's schedule overview."""
```

## Implementation Structure

```
reclaim-mcp-server/
├── pyproject.toml
├── README.md
├── src/
│   └── reclaim_mcp/
│       ├── __init__.py
│       ├── server.py          # Main FastMCP server
│       ├── client.py          # Reclaim API client wrapper
│       ├── models.py          # Pydantic models for requests/responses
│       └── tools/
│           ├── __init__.py
│           ├── tasks.py       # Task-related tools
│           ├── habits.py      # Habit-related tools
│           ├── events.py      # Calendar/event tools
│           └── analytics.py   # Analytics tools
└── tests/
    └── test_server.py
```

## Server Entry Point

```python
# src/reclaim_mcp/server.py
import os
from fastmcp import FastMCP

mcp = FastMCP(
    "Reclaim.ai",
    dependencies=["httpx", "pydantic"]
)

# Environment variable for API key
RECLAIM_API_KEY = os.environ.get("RECLAIM_API_KEY")
RECLAIM_BASE_URL = "https://api.app.reclaim.ai"

# Import and register tools
from .tools import tasks, habits, events, analytics

if __name__ == "__main__":
    mcp.run()
```

## API Client Implementation

```python
# src/reclaim_mcp/client.py
import httpx
from typing import Any

class ReclaimClient:
    def __init__(self, api_key: str, base_url: str = "https://api.app.reclaim.ai"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def get(self, endpoint: str, params: dict = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def post(self, endpoint: str, data: dict) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def patch(self, endpoint: str, data: dict) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def delete(self, endpoint: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}{endpoint}",
                headers=self.headers
            )
            return response.status_code == 200
```

## Key API Endpoints

| Resource | Method | Endpoint |
|----------|--------|----------|
| Tasks | GET | `/api/tasks` |
| Tasks | POST | `/api/tasks` |
| Tasks | PATCH | `/api/tasks/{id}` |
| Tasks | DELETE | `/api/tasks/{id}` |
| Task Complete | POST | `/api/tasks/{id}/complete` |
| Habits | GET | `/api/assist/habits/daily` |
| Habits | POST | `/api/assist/habits/daily` |
| Habits | PATCH | `/api/assist/habits/daily/{id}` |
| Events | GET | `/api/events` |
| Events V2 | GET | `/api/events/v2` |
| Focus Settings | GET | `/api/focus-settings/user` |
| Focus Settings | PATCH | `/api/focus-settings/user/{id}` |
| Analytics | GET | `/api/analytics/user` |
| Calendars | GET | `/api/calendars/primary` |
| User | GET | `/api/users/current` |

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "uv",
      "args": ["run", "--with", "reclaim-mcp-server", "reclaim-mcp-server"],
      "env": {
        "RECLAIM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Or if running from source:

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "uv",
      "args": ["run", "python", "-m", "reclaim_mcp.server"],
      "cwd": "/path/to/reclaim-mcp-server",
      "env": {
        "RECLAIM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Claude Code Configuration

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "python",
      "args": ["-m", "reclaim_mcp.server"],
      "cwd": "/path/to/reclaim-mcp-server",
      "env": {
        "RECLAIM_API_KEY": "${RECLAIM_API_KEY}"
      }
    }
  }
}
```

## Testing

```bash
# Install FastMCP CLI tools
pip install fastmcp

# Run server in dev mode
fastmcp dev src/reclaim_mcp/server.py

# Test with MCP Inspector
fastmcp inspect src/reclaim_mcp/server.py
```

## Known Quirks

1. **Task Status "COMPLETE"**: Reclaim marks tasks as COMPLETE when their scheduled time block ends, even if work isn't finished. Filter explicitly if needed.

2. **Rate Limiting**: Reclaim API may rate limit. Implement exponential backoff.

3. **Unofficial API**: The API is reverse-engineered and may change without notice.

## Dependencies (pyproject.toml)

```toml
[project]
name = "reclaim-mcp-server"
version = "0.1.0"
description = "MCP server for Reclaim.ai calendar integration"
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=2.0.0",
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
]

[project.scripts]
reclaim-mcp-server = "reclaim_mcp.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## References

- FastMCP Docs: https://gofastmcp.com
- FastMCP GitHub: https://github.com/jlowin/fastmcp
- Reclaim SDK (unofficial): https://github.com/labiso-gmbh/reclaim-sdk
- Reclaim Swagger: https://api.app.reclaim.ai/swagger/reclaim-api-0.1.yml
- Existing community server (TypeScript): https://github.com/jj3ny/reclaim-mcp-server
