# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
