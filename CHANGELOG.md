# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-01-01

### Added

- **MCP Best Practices Implementation**:
  - LLM-readable error handling - all tools return clear error strings instead of raising exceptions
  - FastMCP Context injection for operation logging (`ctx.info()`, `ctx.warning()`)
  - Rate limit handling with Retry-After header support (429 responses)
  - TTL caching for read-only endpoints (60-120s TTL with auto-invalidation on mutations)

- **PyPI/Registry Readiness**:
  - PEP 621 `[project]` metadata in pyproject.toml
  - `[project.scripts]` entry point for uvx support
  - Keywords, classifiers, and URLs for package discoverability

- **New Module: `exceptions.py`**:
  - `ReclaimError` - Base exception class
  - `NotFoundError` - 404 responses
  - `RateLimitError` - 429 responses with retry information
  - `APIError` - General API errors

- **New Module: `cache.py`**:
  - `@ttl_cache(ttl)` decorator for caching async function results
  - `invalidate_cache(prefix)` for cache invalidation
  - `get_cache_stats()` for debugging

- **New Tests**:
  - `test_cache.py` - TTL cache, invalidation, error string exclusion
  - Error handling tests in `test_client.py` (404, 429, 401, 500)

- **Documentation**:
  - `SECURITY.md` - Security policy and vulnerability reporting
  - `.env.example` - Environment variable template for new users

### Changed

- All tool functions now accept `ctx: Context` parameter for MCP logging
- All tool return types updated to `dict | str`, `list[dict] | str`, or `bool | str` for error handling
- README updated with uvx installation instructions and best practices section
- Test fixtures now auto-clear cache for test isolation

## [0.4.0] - 2026-01-01

### Added

- **Extended Smart Habits Tools** (7 new tools):
  - `lock_habit_instance` - Lock a habit instance to prevent rescheduling
  - `unlock_habit_instance` - Unlock a habit instance to allow rescheduling
  - `start_habit` - Start a habit session now
  - `stop_habit` - Stop a currently running habit session
  - `enable_habit` - Enable a disabled habit to resume scheduling
  - `disable_habit` - Disable a habit (pause without deleting)
  - `convert_event_to_habit` - Convert a calendar event into a recurring habit

### Fixed

- HTTP client now handles empty response bodies (some API endpoints return no content)
- `list_personal_events` now correctly extracts date from datetime strings (API requires YYYY-MM-DD format)

## [0.3.0] - 2026-01-01

### Added

- **Smart Habits Tools** (7 new tools):
  - `list_habits` - List all smart habits
  - `get_habit` - Get a single habit by lineage ID
  - `create_habit` - Create a new smart habit with scheduling
  - `update_habit` - Update habit properties
  - `delete_habit` - Delete a habit
  - `mark_habit_done` - Mark a habit instance as done
  - `skip_habit` - Skip a habit instance

### Fixed

- **`create_habit` now works correctly** - Multiple API compatibility fixes:
  - Fixed organizer field to use `timePolicyType` (WORK, PERSONAL, MEETING) instead of incorrect `email` field
  - Fixed `idealTime` format normalization from `HH:MM` to `HH:MM:SS` as required by API
  - Fixed `defenseAggression` default from `MEDIUM` to `DEFAULT` (valid values: DEFAULT, NONE, LOW, MEDIUM, HIGH, MAX)

### Changed

- Removed `organizer_email` parameter from `create_habit` (not needed by API)
- Added optional `time_policy_type` parameter (auto-inferred from `event_type` if not provided)
- Updated `docs/API.md` with correct `SmartSeriesOrganizerRequest` schema

## [0.2.0] - 2026-01-01

### Added

- **Calendar & Event Tools** (3 new tools):
  - `list_events` - List calendar events within a time range
  - `list_personal_events` - List Reclaim-managed events (tasks, habits, focus time)
  - `get_event` - Get a single event by calendar ID and event ID

## [0.1.1] - 2026-01-01

### Added

- `list_completed_tasks` tool - List COMPLETE and ARCHIVED tasks
- `get_task` tool - Get single task by ID
- API documentation (`docs/API.md`) with key findings
- Official Reclaim OpenAPI spec (`docs/reclaim-api-0.1.yml`)

### Fixed

- **Time tracking now works correctly** - `add_time_to_task` now uses the correct planner API endpoint (`POST /api/planner/log-work/task/{id}?minutes=X`) instead of PATCH. Time chunks now persist and accumulate properly.

### Changed

- Updated client to support query params in POST requests
- Improved documentation with roadmap and current status

## [0.1.0] - 2026-01-01

### Added

- Initial MCP server implementation with FastMCP
- Task management tools:
  - `list_tasks` - List tasks with status filter
  - `create_task` - Create new tasks with auto-scheduling
  - `update_task` - Update task properties
  - `mark_task_complete` - Complete tasks
  - `delete_task` - Remove tasks
  - `add_time_to_task` - Log time spent
- Async HTTP client for Reclaim.ai API
- Pydantic models for data validation
- CI/CD pipeline with lint and test stages
- GitLab Duo Ready project configuration
