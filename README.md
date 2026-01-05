# Reclaim.ai MCP Server _(UNOFFICIAL)_

[![PyPI version](https://badge.fury.io/py/reclaim-mcp-server.svg)](https://pypi.org/project/reclaim-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **UNOFFICIAL & UNAFFILIATED** – This project is **not** endorsed, sponsored, or supported by Reclaim.ai. It uses Reclaim's public API. Use at your own risk and comply with [Reclaim's Terms of Service](https://reclaim.ai/terms).

A Python MCP (Model Context Protocol) server for [Reclaim.ai](https://reclaim.ai) built with [FastMCP](https://gofastmcp.com).

## Current Status

**Version**: v0.8.0
**Status**: Production-ready with 40 tools (configurable via profiles)

| Feature | Status |
|---------|--------|
| Task Management | ✅ Complete (12 tools) |
| Calendar Events | ✅ Complete (7 tools) |
| Smart Habits | ✅ Complete (14 tools) |
| Analytics | ✅ Complete (2 tools) |
| Focus Time | ✅ Complete (5 tools) |
| Utility | ✅ Complete (2 tools) |

## Requirements

Get your Reclaim.ai API key from: https://app.reclaim.ai/settings/developer

## Installation

### Option 1: PyPI (Recommended)

```bash
pip install reclaim-mcp-server
```

### Option 2: Docker

```bash
docker pull universalamateur/reclaim-mcp-server:latest
```

### Option 3: From Source

```bash
git clone https://gitlab.com/universalamateur1/reclaim-mcp-server.git
cd reclaim-mcp-server
poetry install
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (replace `your_key_here` with your API key):

### Using uvx (Recommended)

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "uvx",
      "args": ["reclaim-mcp-server"],
      "env": {
        "RECLAIM_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Using Docker

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "RECLAIM_API_KEY",
        "universalamateur/reclaim-mcp-server:latest"
      ],
      "env": {
        "RECLAIM_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Using Poetry (from source)

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "/opt/homebrew/bin/poetry",
      "args": [
        "--directory", "/path/to/reclaim-mcp-server",
        "run", "reclaim-mcp-server"
      ],
      "env": {
        "RECLAIM_API_KEY": "your_key_here"
      }
    }
  }
}
```

**Note**: Use the `--directory` flag instead of `cwd` - Claude Desktop doesn't respect the `cwd` setting.

## Tool Profiles

Control which tools are exposed using the `RECLAIM_TOOL_PROFILE` environment variable:

| Profile | Tools | Description |
|---------|-------|-------------|
| `minimal` | 20 | Core tasks + habits basics |
| `standard` | 32 | Core productivity (no niche tools) |
| `full` | 40 | All tools (default) |

```bash
# Use minimal profile
export RECLAIM_TOOL_PROFILE=minimal

# Or with Docker
docker run -e RECLAIM_API_KEY="your_key" -e RECLAIM_TOOL_PROFILE=minimal \
    universalamateur/reclaim-mcp-server
```

**Minimal Profile (20 tools)**: Core task and habit management:
- Tasks: list, create, update, delete, complete, get
- Habits: list, create, update, delete, mark done, skip
- Events: list, list personal, get
- Analytics: get user analytics
- System: health check, verify connection

**Standard Profile (32 tools)**: Adds workflow tools:
- Task workflow: add time, start/stop, prioritize, restart
- Habit workflow: enable/disable
- Focus management: settings, lock/unlock, reschedule
- Analytics: focus insights

**Full Profile (40 tools)**: Adds advanced tools:
- Event management: RSVP, move
- Habit advanced: lock/unlock instances, start/stop sessions, convert from event

## Available Tools

### Tasks (12 tools) ✅

| Tool | Description |
|------|-------------|
| `list_tasks` | List active tasks (excludes completed by default) |
| `list_completed_tasks` | List completed and archived tasks |
| `get_task` | Get a single task by ID |
| `create_task` | Create new task for auto-scheduling |
| `update_task` | Update existing task properties |
| `mark_task_complete` | Mark task as complete |
| `delete_task` | Delete a task |
| `add_time_to_task` | Log time spent on task (uses planner API) |
| `start_task` | Start working on task (timer) |
| `stop_task` | Stop working on task |
| `prioritize_task` | Elevate task priority |
| `restart_task` | Restart a completed task |

### Calendar (5 tools) ✅

| Tool | Description |
|------|-------------|
| `list_events` | List calendar events within a time range |
| `list_personal_events` | List Reclaim-managed events (tasks, habits, focus) |
| `get_event` | Get single event by calendar ID and event ID |
| `set_event_rsvp` | Set RSVP status for event |
| `move_event` | Reschedule event to new time |

### Smart Habits (14 tools) ✅

| Tool | Description |
|------|-------------|
| `list_habits` | List all smart habits |
| `get_habit` | Get a single habit by lineage ID |
| `create_habit` | Create new smart habit for auto-scheduling |
| `update_habit` | Update habit properties |
| `delete_habit` | Delete a habit |
| `mark_habit_done` | Mark a habit instance as done |
| `skip_habit` | Skip a habit instance |
| `lock_habit_instance` | Lock habit instance to prevent rescheduling |
| `unlock_habit_instance` | Unlock habit instance to allow rescheduling |
| `start_habit` | Start a habit session now |
| `stop_habit` | Stop a running habit session |
| `enable_habit` | Enable a disabled habit |
| `disable_habit` | Disable a habit without deleting |
| `convert_event_to_habit` | Convert calendar event to habit |

### Analytics (2 tools) ✅

| Tool | Description |
|------|-------------|
| `get_user_analytics` | Personal productivity analytics (Pro plan) |
| `get_focus_insights` | Focus time analysis and recommendations (Pro plan) |

### Focus Time (5 tools) ✅

| Tool | Description |
|------|-------------|
| `get_focus_settings` | Get current focus time settings |
| `update_focus_settings` | Update focus duration and defense level |
| `lock_focus_block` | Lock focus block to prevent rescheduling |
| `unlock_focus_block` | Unlock focus block |
| `reschedule_focus_block` | Move focus block to new time |

### Utility (2 tools) ✅

| Tool | Description |
|------|-------------|
| `health_check` | Server health check with version info |
| `verify_connection` | Verify API connection by fetching current user |

## MCP Best Practices

This server implements MCP server best practices:

- **Proper Error Handling**: All tools raise `ToolError` exceptions for clear LLM error handling
- **Context Logging**: Uses FastMCP Context for operation logging
- **Rate Limit Handling**: Graceful 429 response handling with Retry-After support
- **TTL Caching**: Read-only endpoints cached (60-120s) with auto-invalidation on mutations
- **Input Validation**: Validates parameters before API calls
- **PEP 621 Metadata**: Full PyPI/Smithery registry compatibility

## Development

```bash
# Install dev dependencies
poetry install --with dev

# Run linting
poetry run black src tests
poetry run isort src tests
poetry run flake8 src tests
poetry run mypy src

# Run tests
poetry run pytest

# Dev mode with hot reload
poetry run fastmcp dev src/reclaim_mcp/server.py

# Inspect tools
poetry run fastmcp inspect src/reclaim_mcp/server.py
```

## Design Principles

1. **[KISS](https://en.wikipedia.org/wiki/KISS_principle)** - Keep It Simple, Stupid
2. **[GitLab Python Standards](https://docs.gitlab.com/ee/development/python_guide/)** - Poetry, Black, mypy, pytest
3. **[MCP Best Practices](https://modelcontextprotocol.io/docs/concepts/tools)** - LLM-readable errors, Context logging, caching
4. **[Semantic Versioning](https://semver.org/)** - Incremental releases, MVP first

## Support

Need help or found a bug? [Open an issue](https://gitlab.com/universalamateur1/reclaim-mcp-server/-/issues/new?issuable_template=Bug) in the repository.

**Note**: Support is provided on a best-effort basis. This is an unofficial community project.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](https://gitlab.com/universalamateur1/reclaim-mcp-server/-/blob/main/CONTRIBUTING.md) for guidelines on:

- Reporting bugs and suggesting features
- Development setup
- Code style and testing
- Merge request process

## License

[MIT](https://gitlab.com/universalamateur1/reclaim-mcp-server/-/blob/main/LICENSE)

## Author

Falko Sieverding ([@UniversalAmateur](https://gitlab.com/UniversalAmateur))

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Reclaim.ai](https://reclaim.ai) - Calendar intelligence platform
