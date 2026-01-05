# Reclaim MCP Server - Agent Guidelines

> **Unofficial** Python MCP server for Reclaim.ai, built with FastMCP.

**Current Version**: v0.8.1 (Released 2026-01-05)
**Next Version**: v0.9.0 (Planning)

---

## Core Principles

### 1. KISS - Keep It Simple, Stupid

AI is a helper, not an authority. Every implementation must be:
- **Simple**: If it feels complex, it probably is. Simplify.
- **Understandable**: Every line merged must be understood by the maintainer.
- **Minimal**: Do the least necessary to solve the problem correctly.

### 2. Quality and Maintainability Over Assumptions

- **Never assume** - If something looks wrong or unclear, **stop and ask**.
- **Pull in help** rather than silently assuming it's fine.
- **Maintainability first** - Code will be read many more times than it's written.

### 3. Explicit Over Implicit

- State what you're doing and why.
- If uncertain, express confidence levels clearly.
- When making tradeoffs, document them.

---

## Project Context

### Purpose

Provides MCP tools for AI assistants to interact with Reclaim.ai's API:

| Category | Tool Count | Description |
|----------|------------|-------------|
| Tasks | 12 | Task CRUD, time tracking, prioritization |
| Habits | 14 | Smart habit management and scheduling |
| Events | 5 | Calendar event operations |
| Focus | 5 | Focus time settings and blocks |
| Analytics | 2 | User productivity analytics |
| Utility | 2 | Health check, server info |

### Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Python | 3.12+ | Modern async features |
| FastMCP | MCP framework | Python-native, modern |
| httpx | Async HTTP | GitLab recommended |
| Pydantic | Validation | Type safety, FastMCP integration |
| Poetry | Dependencies | GitLab standard |

### Directory Structure

```text
src/reclaim_mcp/
├── server.py             # FastMCP server + @tool decorator
├── profiles.py           # Tool profiles (minimal/standard/full)
├── config.py             # Pydantic Settings
├── client.py             # Async httpx client
├── cache.py              # TTL caching with @ttl_cache
├── exceptions.py         # Custom exceptions
├── models.py             # Pydantic validation models
└── tools/
    ├── tasks.py          # Task management
    ├── events.py         # Calendar events
    ├── habits.py         # Smart habits
    ├── analytics.py      # Analytics
    └── focus.py          # Focus time
```

---

## Design Patterns

### Validation: Pydantic-First

**All input validation MUST use Pydantic models in `models.py`.**

```python
# ✅ CORRECT: Centralized validation
class HabitCreate(BaseModel):
    duration_min_mins: int
    duration_max_mins: Optional[int] = None

    @model_validator(mode='after')
    def validate_durations(self):
        if self.duration_max_mins and self.duration_min_mins > self.duration_max_mins:
            raise ValueError("duration_min cannot exceed duration_max")
        return self

# ❌ WRONG: Inline validation in tool functions
async def create_habit(...):
    if duration_min_mins > duration_max_mins:  # Don't do this
        raise ToolError("...")
```

### Error Handling

- Raise `ToolError` from `fastmcp.exceptions` for LLM-friendly errors
- Catch specific exceptions (`ReclaimError`, `NotFoundError`, `RateLimitError`)
- Never use bare `except`
- Log errors with context before re-raising

### Caching Strategy

- Read operations: Use `@ttl_cache(seconds=N)` decorator
- Mutations: Call `invalidate_cache()` to clear stale data

### Async Patterns

- All API calls use `httpx.AsyncClient`
- One client instance per request (not shared)
- Use `async with` for proper resource cleanup

---

## Git Operations Policy

**Agents should NOT execute git commit, push, or tag commands.**

When changes are complete, provide:

```
## Changes Made
- [list changes]

## Suggested Commit Message
feat: [description]

Ready for manual git operations.
```

---

## Reclaim.ai API Reference

### Required Formats

| Field | Format | Example |
|-------|--------|---------|
| `idealTime` | HH:MM:SS | `"09:00:00"` |
| `dueDate` | YYYY-MM-DD | `"2024-12-31"` |
| `datetime` | RFC3339 | `"2024-12-31T09:00:00Z"` |

### Enum Values

```python
DEFENSE_AGGRESSION = ["DEFAULT", "NONE", "LOW", "MEDIUM", "HIGH", "MAX"]
TIME_POLICY_TYPE = ["WORK", "PERSONAL", "MEETING", "ONE_OFF"]
TASK_PRIORITY = ["P1", "P2", "P3", "P4"]
TASK_STATUS = ["NEW", "SCHEDULED", "IN_PROGRESS", "COMPLETE", "ARCHIVED"]
RSVP_STATUS = ["ACCEPTED", "DECLINED", "TENTATIVE", "NEEDS_ACTION"]
```

### API Quirks

- Habit scheduling is **asynchronous** - new habits may not have instances immediately
- Event move uses v1 API endpoint (no calendar_id needed)
- Team analytics tools are plan-gated (removed in v0.7.1)
- `timeChunksSpent` is read-only - use `/api/planner/log-work` to modify

---

## Version Management

**Version MUST be synchronized across ALL locations:**

| File | Location |
|------|----------|
| `pyproject.toml` | `[project] version` |
| `pyproject.toml` | `[tool.poetry] version` |
| `src/reclaim_mcp/__init__.py` | `__version__` |
| `tests/test_server.py` | Version assertion |

After any `pyproject.toml` change:
```bash
poetry lock
```

---

## Development Conventions

### Code Quality Standards

| Tool | Configuration |
|------|---------------|
| Black | 120 line length |
| isort | Black profile |
| flake8 | Max line 120 (via .flake8) |
| mypy | Strict mode |
| Docstrings | Google-style |

### Running Quality Checks

```bash
poetry run black --check src tests
poetry run isort --check-only src tests
poetry run flake8 src tests
poetry run mypy src
```

### Running Tests

```bash
poetry run pytest
poetry run pytest --cov=src/reclaim_mcp
```

---

## Testing Requirements

- Use pytest with pytest-asyncio
- Mock external API calls with monkeypatch
- Target 80%+ code coverage
- Test both success and error paths

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RECLAIM_API_KEY` | Yes | — | Reclaim.ai API token |
| `RECLAIM_BASE_URL` | No | `https://api.app.reclaim.ai` | API base URL |
| `RECLAIM_TOOL_PROFILE` | No | `full` | Profile: minimal/standard/full |

---

## When to Stop and Ask

**Always pause and seek clarification when:**

1. The requested change seems to violate KISS principles
2. You're unsure about the impact on existing functionality
3. The API behavior doesn't match documentation
4. A design decision has multiple valid approaches
5. Test coverage would drop below 80%
6. The change affects version numbers or public interfaces
7. Solution requires > 50 lines of new code
8. Any new dependencies would be added

**Default action when uncertain: Ask, don't assume.**
