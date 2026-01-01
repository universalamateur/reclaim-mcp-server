# Reclaim.ai MCP Server _(UNOFFICIAL)_

> ⚠️ **UNOFFICIAL & UNAFFILIATED** – This project is **not** endorsed, sponsored, or supported by Reclaim.ai. It uses Reclaim's public API. Use at your own risk and comply with [Reclaim's Terms of Service](https://reclaim.ai/terms).

A Python MCP (Model Context Protocol) server for [Reclaim.ai](https://reclaim.ai) built with [FastMCP](https://gofastmcp.com).

## Features

- Task management (list, create, update, complete, delete)
- Calendar event visibility
- Habit tracking
- Focus time configuration
- Time analytics

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
      "command": "poetry",
      "args": ["run", "python", "-m", "reclaim_mcp.server"],
      "cwd": "/path/to/reclaim-mcp-server",
      "env": {
        "RECLAIM_API_KEY": "your_key_here"
      }
    }
  }
}
```

## Available Tools

### Tasks (v0.1.0)

- `list_tasks` - List active tasks (excludes completed by default)
- `list_completed_tasks` - List completed and archived tasks
- `get_task` - Get a single task by ID
- `create_task` - Create new task for auto-scheduling
- `update_task` - Update existing task
- `mark_task_complete` - Mark task as complete
- `delete_task` - Delete a task
- `add_time_to_task` - Log time spent on task (increments existing time)

### Calendar (v0.2.0)

- `list_events` - List calendar events
- `get_free_slots` - Find available time slots

### Habits (v0.3.0)

- `list_habits` - List daily habits
- `create_habit` - Create recurring habit

### Focus (v0.3.0)

- `get_focus_time_settings` - Get focus configuration
- `update_focus_time` - Update focus settings

### Analytics (v1.0.0)

- `get_time_analytics` - Get time tracking summary
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
3. **Duo Project Readiness** - Clear structure for AI assistance
4. **Incremental Releases** - MVP first, features later

## Documentation

See `docs/` folder:

- `API.md` - Reclaim API reference and findings
- `reclaim-api-0.1.yml` - Official OpenAPI spec
- `PLAN.md` - Implementation plan
- `build-spec.md` - Technical specification
- `research.md` - Landscape analysis

## License

MIT

## Author

Falko Sieverding ([@fsieverding](https://gitlab.com/fsieverding))

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [jj3ny/reclaim-mcp-server](https://github.com/jj3ny/reclaim-mcp-server) - Reference TypeScript implementation
- [Reclaim.ai](https://reclaim.ai) - Calendar intelligence platform
