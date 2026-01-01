# Reclaim MCP Server - Implementation Session

## Starting Prompt

Copy this into a new Claude Code session to start implementation:

---

```markdown
# Build Reclaim.ai MCP Server

## Project Context

I'm building a personal MCP server for Reclaim.ai using FastMCP (Python). All planning is complete.

**Key Documents** (read these first):
- `~/git/personal-zettelkasten/project/reclaim-mcp-server/PLAN.md` - Implementation plan
- `~/git/personal-zettelkasten/project/reclaim-mcp-server/build-spec.md` - Technical specification
- `~/git/personal-zettelkasten/project/reclaim-mcp-server/research.md` - Landscape research

**Design Principles**:
1. **KISS** - Keep It Simple, Stupid. Start minimal, add complexity only when needed.
2. **GitLab Python Standards** - Poetry, Black, isort, flake8, pylint, mypy, pytest
3. **Duo Project Readiness** - Aligned with [SA Initiative #615](https://gitlab.com/gitlab-com/customer-success/solutions-architecture-leaders/sa-initiatives/-/issues/615)
4. **Incremental Releases** - v0.1.0 (tasks) → v0.2.0 (calendar) → v0.3.0 (habits) → v1.0.0

## Today's Goal

Complete **Phase 1: Project Setup** and start **Phase 2: Core Infrastructure**

### Phase 1 Tasks:
1. Create project on GitLab: https://gitlab.com/universalamateur1/reclaim-mcp-server
2. Clone to `~/git/reclaim-mcp-server/`
3. Initialize with Poetry
4. Create pyproject.toml (copy from PLAN.md)
5. Create .gitlab-ci.yml (copy from PLAN.md)
6. Create minimal src/reclaim_mcp structure
7. Push and verify CI passes

### Phase 2 Tasks:
1. Implement config.py with Pydantic Settings
2. Implement client.py with async httpx
3. Implement models.py with Task model
4. Add basic tests

## Before Starting

1. Read the PLAN.md to understand the full scope
2. Read the build-spec.md for API details
3. Check that Poetry is installed: `poetry --version`
4. Have my Reclaim API key ready (from https://app.reclaim.ai/settings/developer)

## Let's Go!

Start by reading the plan and spec files, then walk me through each step of Phase 1.
```

---

## Pre-Session Checklist

Before starting the implementation session:

- [ ] Poetry installed (`brew install poetry` or `pipx install poetry`)
- [ ] Git configured for GitLab
- [ ] Reclaim API key obtained from https://app.reclaim.ai/settings/developer
- [ ] Store API key: `export RECLAIM_API_KEY="rclm_..."`
- [ ] GitLab project created (or ready to create)

## Expected Session Outcome

By end of session:
- [ ] GitLab repo created and cloned
- [ ] Poetry project initialized
- [ ] CI pipeline passing (lint + test)
- [ ] Basic client.py working with real API
- [ ] Ready to start Phase 3 (Task tools)

## Notes

- This is a **personal side project** - don't over-engineer
- The existing TypeScript server (jj3ny) has 14 tools - we'll match feature parity incrementally
- Reclaim API is unofficial/reverse-engineered - may change
- Focus on getting `list_tasks` working end-to-end first
