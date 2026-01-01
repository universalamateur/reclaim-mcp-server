# Project Context

This is a Python MCP (Model Context Protocol) server for Reclaim.ai integration, built with FastMCP.

## Purpose

Provides MCP tools for AI assistants to interact with Reclaim.ai's task management API, enabling:
- Task listing and filtering
- Task creation with auto-scheduling
- Task updates and completion
- Time tracking

## Directory Structure

```
src/reclaim_mcp/
├── __init__.py           # Package version
├── server.py             # FastMCP server and tool definitions
├── config.py             # Pydantic Settings for API configuration
├── client.py             # Async httpx client for Reclaim API
├── models.py             # Pydantic models for data validation
└── tools/
    └── tasks.py          # Task management functions

tests/
├── conftest.py           # Pytest fixtures
├── test_client.py        # API client tests
├── test_models.py        # Model validation tests
└── test_server.py        # Server tests
```

## Technology Stack

- **Python**: 3.10+
- **FastMCP**: MCP server framework
- **httpx**: Async HTTP client
- **Pydantic**: Data validation and settings
- **Poetry**: Dependency management

## Development Conventions

### Code Style

- **Formatter**: Black (120 line length)
- **Import sorting**: isort (Black profile)
- **Linting**: flake8
- **Type checking**: mypy (strict mode)
- **Docstrings**: Google-style

### Patterns

- All API calls are async using `httpx.AsyncClient`
- Configuration via environment variables with `RECLAIM_` prefix
- Pydantic models use `Field(alias="camelCase")` for API compatibility
- Tools return raw dicts, not Pydantic models (for MCP serialization)

### Error Handling

- Use `httpx.Response.raise_for_status()` for HTTP errors
- Catch specific exceptions, not bare `except`
- Log errors with context before re-raising

## Testing Requirements

- Use pytest with pytest-asyncio for async tests
- Mock external API calls with monkeypatch
- Target 80%+ code coverage
- Test both success and error paths

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RECLAIM_API_KEY` | Yes | Reclaim.ai API token |
| `RECLAIM_BASE_URL` | No | API base URL (default: https://api.app.reclaim.ai) |

## Running Locally

```bash
# Install dependencies
poetry install

# Run linting
poetry run black --check src tests
poetry run isort --check-only src tests
poetry run flake8 src tests
poetry run mypy src

# Run tests
poetry run pytest

# Start the MCP server
poetry run python -m reclaim_mcp.server
```

## Agent Instructions

### Git Operations

**Important**: The owner handles all git commit, push, and tagging operations manually.

Do NOT:

- Execute `git commit` commands
- Execute `git push` commands
- Execute `git tag` commands

When ready to commit, provide:

- A summary of changes made
- A suggested commit message
- Let the user handle the actual git operations

### MCP Server Testing

The MCP server `reclaim-dev` runs as a separate process. Code changes require:

1. Testing via direct Python calls (`poetry run python -c "..."`)
2. Or restarting Claude Code session to reload the MCP server

### API Quirks (Reclaim.ai)

- `idealTime` format must include seconds: `HH:MM:SS` (not `HH:MM`)
- `defenseAggression` valid values: `DEFAULT`, `NONE`, `LOW`, `MEDIUM`, `HIGH`, `MAX`
- `timePolicyType` valid values: `WORK`, `PERSONAL`, `MEETING`, `ONE_OFF`
- Habit scheduling happens asynchronously - newly created habits may not have scheduled instances immediately
