# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
