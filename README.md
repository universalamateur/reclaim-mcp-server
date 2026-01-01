# Reclaim.ai MCP Server _(UNOFFICIAL)_

> **UNOFFICIAL & UNAFFILIATED** – This project is **not** endorsed, sponsored, or supported by Reclaim.ai. It uses Reclaim's public API. Use at your own risk and comply with [Reclaim's Terms of Service](https://reclaim.ai/terms).

A Python MCP (Model Context Protocol) server for [Reclaim.ai](https://reclaim.ai) built with [FastMCP](https://gofastmcp.com).

## Current Status

**Version**: v0.5.0
**Status**: Production-ready with best practices

| Feature | Status |
|---------|--------|
| Task Management | ✅ Complete (9 tools) |
| Calendar Events | ✅ Complete (3 tools) |
| Smart Habits | ✅ Complete (14 tools) |
| Best Practices | ✅ Complete (v0.5.0) |
| Focus Settings | 🔲 Planned (v0.6.0) |
| Analytics | 🔲 Planned (v0.7.0) |

## Installation

### Option 1: uvx (Recommended)

```bash
# Run directly without installation
uvx --from git+https://gitlab.com/universalamateur1/reclaim-mcp-server.git reclaim-mcp-server
```

### Option 2: Poetry

```bash
# Clone the repo
git clone https://gitlab.com/universalamateur1/reclaim-mcp-server.git
cd reclaim-mcp-server

# Install dependencies
poetry install

# Set your API key
export RECLAIM_API_KEY="your_key_here"
# Get key from: https://app.reclaim.ai/settings/developer

# Run the server
poetry run reclaim-mcp-server
```

## Claude Desktop Configuration

### Using uvx

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "uvx",
      "args": [
        "--from", "git+https://gitlab.com/universalamateur1/reclaim-mcp-server.git",
        "reclaim-mcp-server"
      ],
      "env": {
        "RECLAIM_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Using Poetry

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

## Available Tools

### Tasks (9 tools) ✅

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
| `health_check` | Server health check |

### Calendar (3 tools) ✅

| Tool | Description |
|------|-------------|
| `list_events` | List calendar events within a time range |
| `list_personal_events` | List Reclaim-managed events (tasks, habits, focus) |
| `get_event` | Get single event by calendar ID and event ID |

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

## v0.5.0 Best Practices

This release implements MCP server best practices:

- **LLM-Readable Errors**: All tools return clear error strings instead of raising exceptions
- **Context Logging**: Uses FastMCP Context for operation logging
- **Rate Limit Handling**: Graceful 429 response handling with Retry-After support
- **TTL Caching**: Read-only endpoints cached (60-120s) with auto-invalidation on mutations
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

1. **KISS** - Keep It Simple, Stupid
2. **GitLab Python Standards** - Poetry, Black, mypy, pytest
3. **MCP Best Practices** - LLM-readable errors, Context logging, caching
4. **Incremental Releases** - MVP first, features later

## Documentation

See `docs/` folder:

- `API.md` - Reclaim API reference and key findings
- `reclaim-api-0.1.yml` - Official OpenAPI spec (29k lines)
- `PLAN.md` - Implementation plan
- `build-spec.md` - Technical specification
- `research.md` - Landscape analysis
- `best_practices_developing_MCP_servers_fastmcp.md` - MCP best practices guide

## Roadmap

| Version | Features | Status |
|---------|----------|--------|
| v0.1.0 | Task CRUD, completion, time tracking | ✅ Released |
| v0.1.1 | Fixed time tracking, added get_task, list_completed_tasks | ✅ Released |
| v0.2.0 | Calendar events (list, get) | ✅ Released |
| v0.3.0 | Smart Habits (7 tools) | ✅ Released |
| v0.4.0 | Extended Habits (14 tools total) | ✅ Released |
| v0.5.0 | Best practices + PyPI readiness | ✅ Released |
| v0.6.0 | Focus time settings | 🔲 Planned |
| v0.7.0 | Analytics, scheduling links | 🔲 Planned |

## License

[MIT](./LICENSE)

## Author

Falko Sieverding ([@UniversalAmateur](https://gitlab.com/UniversalAmateur))

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Reclaim.ai](https://reclaim.ai) - Calendar intelligence platform
