# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.11.0] - 2026-02-22

### Added

- **Scheduling Tools** (2 new tools):
  - `get_working_hours` — Read working hours and availability schemes (`GET /api/timeschemes`)
  - `find_available_times` — Find available meeting times for attendees (`POST /api/availability/suggested-times`)
- `SuggestedTimesRequest` Pydantic model with date window validation

### Changed

- `get_working_hours` added to **standard** profile (read-only scheduling visibility)
- `find_available_times` added to **full** profile (meeting scheduling action)

**Total tools: 49** (minimal: 22, standard: 39, full: 49)

## [0.9.2] - 2026-02-15

### Fixed

- **`update_task` zero time chunks**: Durations under 15 minutes now correctly produce
  minimum 1 time chunk instead of 0 (matching `create_task` behavior)
- **`FocusSettingsUpdate` validation**: Duration ordering checks now use `is not None`
  instead of truthiness, fixing a logic error where valid values could be skipped
- **Event caching**: Added `@ttl_cache(ttl=60)` to `list_events` and `list_personal_events`
  to match existing `invalidate_cache` calls (were previously no-ops)

**Total tools: 40** (unchanged)

## [0.9.1] - 2026-01-06

### Fixed

- **MCP Registry compatibility**: README now includes `mcp-name` marker in PyPI package
  - Enables listing on [modelcontextprotocol.io](https://modelcontextprotocol.io)

## [0.9.0] - 2026-01-06

### Added

- **MCP Registry discoverability**:
  - `smithery.yaml` - Smithery.ai deployment config (stdio transport, uvx-based)
  - `server.json` - MCP Registry metadata
  - Listed on [Smithery](https://smithery.ai/server/universalamateur/reclaim-mcp-server) and [Glama](https://glama.ai/mcp/servers/@universalamateur/reclaim-mcp-server)
- **GitHub mirror**: https://github.com/universalamateur/reclaim-mcp-server

### Changed

- **CI: Fully automated release pipeline** - all publish jobs now run automatically on tag push
  - `publish-gitlab-package`, `publish-pypi`, `publish-dockerhub`, `create-release` trigger automatically
  - `publish-testpypi` now runs on merge requests only (for CI validation)

### Fixed

- **CI: `create-release` job** now uses native `release:` keyword instead of `glab` CLI
  - No longer requires PAT (`GITLAB_TOKEN`) - works with `CI_JOB_TOKEN`
  - Uploads artifacts to Generic Package Registry for permanent download URLs
- **README badges** now display horizontally on PyPI (single-line format)

## [0.8.1] - 2026-01-05

### Added

- **Multi-platform Docker builds**: Now building for `linux/amd64` and `linux/arm64`
  - Native support for Apple Silicon (M1/M2/M3) without Rosetta 2 emulation
- **Docker pull verification**: Automatic CI job verifies images are pullable after publish
- **Registry caching**: Faster Docker rebuilds via `--cache-from`/`--cache-to`
- **Tool reference docs**: New `docs/TOOLS.md` with complete tool documentation

### Changed

- Docker base image upgraded from `docker:24.0.5` to `docker:27`
- Build and push consolidated into single `docker buildx` command
- Container scanning now scans from registry instead of tarball artifact
- GitLab Container Registry publish merged into `build-docker` job
- **README refactored**: Shorter, badges, "What You Can Do" examples, collapsible sections

### Fixed

- ARM64 (Apple Silicon) compatibility for Docker images
- Docker buildx TLS compatibility in GitLab CI (disabled TLS for docker-container driver)

**Total tools: 40** (unchanged)

## [0.8.0] - 2026-01-04

### Added

- **Tool Profiles**: Control which tools are exposed via `RECLAIM_TOOL_PROFILE` environment variable
  - `minimal`: 20 core tools (tasks, habits basics, events)
  - `standard`: 32 tools (adds workflow and focus management)
  - `full`: 40 tools (all tools, default)
- **Docker Distribution**: Multi-stage build with non-root user
  - Available at `universalamateur/reclaim-mcp-server`
- **Multi-Registry Publishing**: GitLab CI pipeline for PyPI, TestPyPI, GitLab Package Registry, GitLab Container Registry, and DockerHub
- **OIDC Trusted Publishing**: Secure PyPI releases without token secrets
- **Trivy Container Scanning**: Free vulnerability scanning for Docker images (HIGH/CRITICAL)
- **CI Workflow Optimization**: Use `$CI_COMMIT_REF_PROTECTED` to prevent duplicate pipelines

### Changed

- Custom `@tool` decorator in server.py for profile-based registration
- Updated documentation for PyPI and Docker installation options

### Fixed

- **MED-001/MED-002**: `delete_habit`, `disable_habit`, and `delete_task` now properly
  reject non-existent resource IDs with clear error messages instead of silently succeeding.
  - `client.delete()` now raises `NotFoundError` for 404 responses (consistent with other HTTP methods)
  - Added `NotFoundError` handling in all delete/disable operations

### Removed

- **`pin_event` / `unpin_event` tools**: Upstream Reclaim.ai API returns HTTP 500
  for these endpoints. Tools removed until Reclaim fixes the API.
- **`HOURS_DEFENDED` / `FOCUS_WORK_BALANCE` metrics**: V3 Analytics API returns
  400 Bad Request for these metric names. Use `DURATION_BY_CATEGORY` or
  `DURATION_BY_DATE_BY_CATEGORY` instead.

**Total tools: 40** (reduced from 42 - removed broken upstream features)

## [0.7.5] - 2026-01-03

### Fixed

- **CRIT-001**: Fixed validation bypass for `Optional[int]` fields with `Field(gt=0)`
  - Pydantic V2 doesn't enforce `gt=0` constraint on Optional types
  - Added explicit `@field_validator` for 8 affected fields across models
  - Affected: `TaskCreate`, `TaskUpdate`, `HabitCreate`, `HabitUpdate`, `FocusSettingsUpdate`

### Changed

- **OPP-001**: Extracted duplicated `format_validation_errors` helper to shared `utils.py`
  - Reduces code duplication across 5 tool files
  - Single source of truth for validation error formatting

**Total tools: 42** (unchanged)

## [0.7.4] - 2026-01-03

### Fixed

- **BREAKING**: `set_event_rsvp` now works correctly
  - Changed HTTP method from POST to PUT
  - Changed body field from `rsvpStatus` to `responseStatus`
  - Fixed enum values to PascalCase (`Accepted`, `Declined`, `TentativelyAccepted`, `NeedsAction`)
  - Added `send_updates` parameter (default: true)

- **BREAKING**: `move_event` now works correctly
  - Switched to v1 API endpoint (`/api/planner/event/move/{event_id}`)
  - Removed `calendar_id` parameter (no longer needed)
  - Parameters now sent as query params instead of body

- **BREAKING**: `get_user_analytics` now works correctly
  - Changed `metric_names` (optional list) to `metric_name` (required single value)
  - Only one metric can be retrieved per API call

### Added

- `put()` method to HTTP client for RSVP operations
- Date validation for `due_date` in TaskCreate/TaskUpdate (must be YYYY-MM-DD format)

**Total tools: 42** (unchanged)

## [0.7.3] - 2026-01-02

### Fixed

- `list_personal_events` now returns correct data (was using wrong date param format)
- Task validation errors now provide clear messages

### Added

- `verify_connection` tool - Verify API connection and get current user info

**Total tools: 42**

## [0.7.2] - 2026-01-02

### Changed

- Centralized Pydantic validation for all input models
- Enhanced error handling with structured error messages
- Added model validators for complex constraints

## [0.7.1] - 2026-01-02

### Fixed

- `get_focus_settings` now correctly returns `list[dict]` (API returns list of focus settings)
- `create_habit` now validates that `ideal_days` cannot be used with DAILY frequency
- All 41 tools now raise proper `ToolError` exceptions instead of returning error strings

### Removed

- `get_team_analytics` - plan-gated feature causing user confusion
- `export_team_analytics` - plan-gated feature causing user confusion

### Changed

- Refactored all tool error handling from `dict | str` return types to proper exceptions
- Added input validation for duration, priority, and frequency parameters
- Added `RateLimitError` handling to all tools

**Total tools: 41** (reduced from 43)

## [0.7.0] - 2026-01-02

### Added

- **Analytics Tools** (4 new tools):
  - `get_user_analytics` - Personal productivity analytics with time breakdowns
  - `get_focus_insights` - Focus time analysis and recommendations
  - `get_team_analytics` - Team productivity metrics (requires team plan)
  - `export_team_analytics` - Export team data to CSV/JSON format

- **Focus Time Tools** (5 new tools):
  - `get_focus_settings` - Get current focus time configuration
  - `update_focus_settings` - Update focus duration and defense aggression
  - `lock_focus_block` - Lock a focus block to prevent rescheduling
  - `unlock_focus_block` - Unlock a focus block to allow rescheduling
  - `reschedule_focus_block` - Move a focus block to a different time

- **New Modules**:
  - `src/reclaim_mcp/tools/analytics.py` - Analytics functionality
  - `src/reclaim_mcp/tools/focus.py` - Focus time management

**Total tools: 43**

## [0.6.0] - 2026-01-02

### Added

- **Task Planner Tools** (4 new tools):
  - `start_task` - Start working on a task (marks IN_PROGRESS, starts timer)
  - `stop_task` - Stop working on a task (pauses timer)
  - `prioritize_task` - Elevate task priority (triggers rescheduling)
  - `restart_task` - Restart a completed/archived task

- **Event Planner Tools** (4 new tools):
  - `pin_event` - Lock event at its current time
  - `unpin_event` - Allow event to be rescheduled by AI
  - `set_event_rsvp` - Set RSVP status (ACCEPTED, DECLINED, TENTATIVE, NEEDS_ACTION)
  - `move_event` - Reschedule event to a new time slot

**Total tools: 34**

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
