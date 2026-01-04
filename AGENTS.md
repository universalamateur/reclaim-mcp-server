# Project Context

This is a Python MCP (Model Context Protocol) server for Reclaim.ai integration, built with FastMCP.

**Current Version**: v0.8.0 (42 tools, configurable via profiles)

## Purpose

Provides MCP tools for AI assistants to interact with Reclaim.ai's API, enabling:
- Task management (12 tools)
- Calendar events (7 tools)
- Smart habits (14 tools)
- Analytics (2 tools)
- Focus time (5 tools)
- Utility (2 tools)

## Directory Structure

```
src/reclaim_mcp/
├── __init__.py           # Package version
├── server.py             # FastMCP server + custom @tool decorator
├── profiles.py           # Tool profile definitions (minimal/standard/full)
├── config.py             # Pydantic Settings (API + RECLAIM_TOOL_PROFILE)
├── client.py             # Async httpx client for Reclaim API
├── cache.py              # TTL caching with @ttl_cache
├── exceptions.py         # Custom exceptions
├── models.py             # Pydantic models for data validation
└── tools/
    ├── tasks.py          # Task management (12 tools)
    ├── events.py         # Calendar events (7 tools)
    ├── habits.py         # Smart habits (14 tools)
    ├── analytics.py      # Analytics (2 tools)
    └── focus.py          # Focus time (5 tools)

tests/
├── conftest.py           # Pytest fixtures
├── test_client.py        # API client tests
├── test_models.py        # Model validation tests
├── test_events.py        # Event tools tests
└── test_server.py        # Server tests (includes version assertion)
```

## Technology Stack

- **Python**: 3.12+
- **FastMCP**: MCP server framework
- **httpx**: Async HTTP client
- **Pydantic**: Data validation and settings
- **Poetry**: Dependency management

## Version Management

**Version MUST be updated in ALL locations on every release:**

| File | Location |
|------|----------|
| `pyproject.toml` | `[project] version` |
| `pyproject.toml` | `[tool.poetry] version` |
| `src/reclaim_mcp/__init__.py` | `__version__` |
| `tests/test_server.py` | Version assertion |

Note: `health_check` returns version automatically via `__version__` import.

Failure to keep these aligned causes version confusion for clients.

**After any `pyproject.toml` change, run `poetry lock` to sync the lock file:**

```bash
poetry lock
```

This includes version bumps, dependency changes, or any `[tool.poetry]` modifications.
Failing to do this will cause CI pipeline failures.

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
| `RECLAIM_TOOL_PROFILE` | No | Tool profile: minimal (20), standard (32), full (42, default) |

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
