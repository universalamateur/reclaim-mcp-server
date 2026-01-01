# Reclaim.ai MCP Server _(UNOFFICIAL)_

> ⚠️ **UNOFFICIAL & UNAFFILIATED** – This project is **not** endorsed, sponsored, or supported by Reclaim.ai. It uses Reclaim's public API. Use at your own risk and comply with [Reclaim's Terms of Service](https://reclaim.ai/terms).

A Python MCP (Model Context Protocol) server for [Reclaim.ai](https://reclaim.ai) built with [FastMCP](https://gofastmcp.com).

## Current Status

**Version**: v0.1.1
**Status**: Task management fully working

| Feature | Status |
|---------|--------|
| Task Management | ✅ Complete (9 tools) |
| Calendar Events | 🔲 Planned (v0.2.0) |
| Habits & Focus | 🔲 Planned (v0.3.0) |
| Analytics | 🔲 Planned (v1.0.0) |

## Installation

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
poetry run python -m reclaim_mcp.server
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "reclaim": {
      "command": "/opt/homebrew/bin/poetry",
      "args": [
        "--directory", "/path/to/reclaim-mcp-server",
        "run", "python", "-m", "reclaim_mcp.server"
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

### Tasks (v0.1.1) ✅

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

### Calendar (v0.2.0) 🔲

- `list_events` - List calendar events in date range
- `get_event` - Get single calendar event
- `get_free_slots` - Find available time slots

### Habits & Focus (v0.3.0) 🔲

- `list_habits` - List smart habits
- `create_habit` - Create recurring habit
- `mark_habit_done` - Mark habit done for today
- `get_focus_settings` - Get focus time configuration
- `update_focus_settings` - Update focus settings

### Analytics (v1.0.0) 🔲

- `get_time_analytics` - Get time tracking summary
- `get_focus_insights` - Focus time insights
- `list_scheduling_links` - List scheduling links

## Development

```bash
# Install dev dependencies
poetry install --with dev

# Run linting
poetry run black src tests
poetry run isort src tests
poetry run flake8 src tests
poetry run mypy src

# Run tests (28 tests)
poetry run pytest

# Dev mode with hot reload
poetry run fastmcp dev src/reclaim_mcp/server.py

# Inspect tools
poetry run fastmcp inspect src/reclaim_mcp/server.py
```

## Design Principles

1. **KISS** - Keep It Simple, Stupid
2. **GitLab Python Standards** - Poetry, Black, mypy, pytest
3. **Duo Project Readiness** - Clear structure for AI assistance
4. **Incremental Releases** - MVP first, features later

## Documentation

See `docs/` folder:

- `API.md` - Reclaim API reference and key findings
- `reclaim-api-0.1.yml` - Official OpenAPI spec (29k lines)
- `PLAN.md` - Implementation plan
- `build-spec.md` - Technical specification
- `research.md` - Landscape analysis

## Roadmap

| Version | Features | Status |
|---------|----------|--------|
| v0.1.0 | Task CRUD, completion, time tracking | ✅ Released |
| v0.1.1 | Fixed time tracking, added get_task, list_completed_tasks | ✅ Ready |
| v0.2.0 | Calendar events, free slots | 🔲 Planned |
| v0.3.0 | Habits, focus time settings | 🔲 Planned |
| v1.0.0 | Analytics, scheduling links, PyPI | 🔲 Planned |

## License

MIT

## Author

Falko Sieverding ([@fsieverding](https://gitlab.com/fsieverding))

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [jj3ny/reclaim-mcp-server](https://github.com/jj3ny/reclaim-mcp-server) - Reference TypeScript implementation
- [Reclaim.ai](https://reclaim.ai) - Calendar intelligence platform
