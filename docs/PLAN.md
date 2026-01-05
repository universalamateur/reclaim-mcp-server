# Reclaim.ai MCP Server - Implementation Plan

**Status**: v0.8.0 - 40 Tools (configurable via profiles)
**Date**: 2026-01-04
**Repo**: https://gitlab.com/universalamateur1/reclaim-mcp-server

---

## Design Principles

### 1. KISS (Keep It Simple, Stupid)
- Start with minimal viable implementation
- No premature optimization
- Simple code > clever code
- Only add complexity when needed

### 2. GitLab Python Standards
Follow [GitLab Python Development Guidelines](https://docs.gitlab.com/development/python_guide/):
- **Poetry** for dependency management
- **Black** (line-length=120) + **isort** for formatting
- **flake8** + **pylint** + **mypy** for linting/type checking
- **pytest** + **pytest-cov** for testing
- **pyproject.toml** as single config file

### 3. Duo Project Readiness Aligned
This project follows GitLab Duo-Ready project standards:
- Well-structured for AI code suggestions
- Clear module boundaries
- Comprehensive type hints
- Good test coverage
- Documentation in code

### 4. FastMCP Patterns
- Use FastMCP 2.0 decorators (`@mcp.tool`, `@mcp.resource`)
- Async httpx client for API calls
- Pydantic models for request/response validation
- Environment-based configuration (no hardcoded secrets)

### 5. Incremental Releases
- **v0.1.0**: Tasks only (6 tools) - usable MVP
- **v0.2.0**: Add Calendar (8 tools)
- **v0.3.0**: Add Habits + Focus (12 tools)
- **v1.0.0**: Full spec (14 tools) + resources + polish

---

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | FastMCP 2.0 | Modern MCP server framework, Python-native |
| HTTP Client | httpx (async) | GitLab recommended, async support |
| Validation | Pydantic v2 | Type safety, FastMCP integration |
| Package Mgr | Poetry | GitLab standard |
| Linting | Black, isort, flake8, pylint, mypy | GitLab standard |
| Testing | pytest, pytest-cov | GitLab standard |
| CI/CD | GitLab CI | Native integration |

---

## CI/CD Pipeline

### Pipeline Stages

```
lint → test → security → build → publish → release
```

### Multi-Registry Publishing (v0.8.0+)

| Registry | Purpose | Auth Method |
|----------|---------|-------------|
| **PyPI** | Public Python package | OIDC Trusted Publishing |
| **TestPyPI** | Pre-release validation | OIDC Trusted Publishing |
| **GitLab Package Registry** | Internal/enterprise | `$CI_JOB_TOKEN` (auto) |
| **GitLab Container Registry** | Docker images | `$CI_REGISTRY_*` (auto) |
| **DockerHub** | Public Docker images | Access token |

### Key Features

- **OIDC Trusted Publishing**: No PyPI API tokens needed - GitLab exchanges OIDC tokens directly
- **Manual publish triggers**: All publish jobs require manual trigger to prevent accidental releases
- **TestPyPI → PyPI flow**: Validate packages on TestPyPI before production release
- **GitLab Environments**: Track deployments to `release-test`, `release`, and `docker`
- **Container scanning**: Trivy scans for HIGH/CRITICAL vulnerabilities

### Release Process

1. Update version in 4 locations + `poetry lock`
2. Update CHANGELOG.md
3. Commit to main, create/push tag `vX.Y.Z`
4. Manually trigger publish jobs in GitLab UI
5. Create GitLab Release with asset links

See [RELEASING.md](/RELEASING.md) for detailed instructions.

---

## Project Structure

```
reclaim-mcp-server/
├── .gitlab-ci.yml              # CI/CD pipeline
├── Dockerfile                  # Multi-stage Docker build
├── pyproject.toml              # Poetry + tool configs
├── README.md                   # Usage documentation
├── CONTRIBUTING.md             # Contribution guidelines
├── RELEASING.md                # Release process documentation
├── LICENSE                     # MIT
├── src/
│   └── reclaim_mcp/
│       ├── __init__.py
│       ├── server.py           # FastMCP server + custom @tool decorator
│       ├── profiles.py         # Tool profiles (minimal/standard/full)
│       ├── client.py           # Reclaim API client (httpx)
│       ├── config.py           # Environment/settings
│       ├── cache.py            # TTL caching with @ttl_cache
│       ├── exceptions.py       # Custom exceptions
│       ├── models.py           # Pydantic models
│       └── tools/
│           ├── __init__.py
│           ├── tasks.py        # 12 task tools
│           ├── events.py       # 5 event tools
│           ├── habits.py       # 14 habit tools
│           ├── focus.py        # 5 focus tools
│           └── analytics.py    # 2 analytics tools
├── tests/
│   ├── conftest.py
│   ├── test_client.py
│   ├── test_tasks.py
│   └── test_events.py
└── scripts/
    └── dev.sh                  # Local dev helper
```

---

## Implementation Phases

### Phase 1: Project Setup (v0.0.1)
**Goal**: Skeleton project with working CI

1. Create project on gitlab.com/universalamateur1/reclaim-mcp-server
2. Clone to `~/git/reclaim-mcp-server/`
3. Initialize with Poetry
4. Create pyproject.toml with all tool configs
5. Set up .gitlab-ci.yml with lint + test stages
6. Create minimal src/reclaim_mcp structure
7. Push and verify CI passes

**Files to create**:
- `pyproject.toml`
- `.gitlab-ci.yml`
- `src/reclaim_mcp/__init__.py`
- `src/reclaim_mcp/server.py` (minimal)
- `README.md`
- `LICENSE`

### Phase 2: Core Infrastructure (v0.0.2)
**Goal**: Working API client and config

1. Implement `config.py` with Pydantic Settings
2. Implement `client.py` with async httpx
3. Implement `models.py` with Task Pydantic model
4. Add basic tests with mocked responses

**Files to create**:
- `src/reclaim_mcp/config.py`
- `src/reclaim_mcp/client.py`
- `src/reclaim_mcp/models.py`
- `tests/conftest.py`
- `tests/test_client.py`

### Phase 3: Task Tools (v0.1.0) - MVP Release
**Goal**: 6 working task tools in Claude Desktop

Tools:
- `list_tasks` - List all tasks with status filter
- `create_task` - Create new task
- `update_task` - Update existing task
- `mark_task_complete` - Mark as complete
- `delete_task` - Delete task
- `add_time_to_task` - Log time spent

**Files to create**:
- `src/reclaim_mcp/tools/__init__.py`
- `src/reclaim_mcp/tools/tasks.py`
- `tests/test_tasks.py`

**Deliverable**: Tagged v0.1.0 release, Claude Desktop working

### Phase 4: Calendar Tools (v0.2.0)
**Goal**: Add calendar visibility

Tools:
- `list_events` - List calendar events
- `get_free_slots` - Find available time

Resources:
- `reclaim://today` - Today's schedule
- `reclaim://week` - Week overview

### Phase 5: Habits & Focus (v0.3.0)
**Goal**: Complete daily workflow tools

Tools:
- `list_habits` - List habits
- `create_habit` - Create habit
- `get_focus_time_settings` - Get focus config
- `update_focus_time` - Update focus config

### Phase 6: Polish & Publish (v1.0.0)
**Goal**: Production-ready release

- `get_time_analytics` - Analytics tool
- `list_scheduling_links` - Scheduling links
- `reclaim://tasks/active` - Active tasks resource
- Error handling polish
- Documentation
- PyPI publication (optional)

---

## API Endpoints Reference

| Tool | Method | Endpoint |
|------|--------|----------|
| list_tasks | GET | `/api/tasks` |
| create_task | POST | `/api/tasks` |
| update_task | PATCH | `/api/tasks/{id}` |
| mark_task_complete | POST | `/api/tasks/{id}/complete` |
| delete_task | DELETE | `/api/tasks/{id}` |
| list_events | GET | `/api/events` |
| list_habits | GET | `/api/assist/habits/daily` |
| create_habit | POST | `/api/assist/habits/daily` |
| get_focus_settings | GET | `/api/focus-settings/user` |
| get_analytics | GET | `/api/analytics/user` |

---

## Configuration Templates

### pyproject.toml

```toml
[tool.poetry]
name = "reclaim-mcp-server"
version = "0.1.0"
description = "MCP server for Reclaim.ai calendar integration"
authors = ["Falko Sieverding"]
license = "MIT"
readme = "README.md"
packages = [{include = "reclaim_mcp", from = "src"}]

[tool.poetry.dependencies]
python = "^3.10"
fastmcp = "^2.0.0"
httpx = "^0.24.0"
pydantic = "^2.0.0"
pydantic-settings = "^2.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-cov = "^4.0.0"
pytest-asyncio = "^0.21.0"
black = "^23.0.0"
isort = "^5.12.0"
flake8 = "^6.0.0"
pylint = "^2.17.0"
mypy = "^1.0.0"

[tool.poetry.scripts]
reclaim-mcp-server = "reclaim_mcp.server:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 120

[tool.isort]
profile = "black"
line_length = 120

[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
strict = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### .gitlab-ci.yml

```yaml
stages:
  - lint
  - test

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - .venv

.poetry-setup:
  before_script:
    - pip install poetry
    - poetry config virtualenvs.in-project true
    - poetry install

lint:
  stage: lint
  image: python:3.10
  extends: .poetry-setup
  script:
    - poetry run black --check src tests
    - poetry run isort --check-only src tests
    - poetry run flake8 src tests
    - poetry run mypy src

test:
  stage: test
  image: python:3.10
  extends: .poetry-setup
  script:
    - poetry run pytest --cov=src/reclaim_mcp --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

### Claude Desktop Config

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

---

## Testing Strategy

1. **Unit tests**: Mock httpx responses, test tool logic
2. **Integration tests**: Real API calls (manual, not CI)
3. **MCP Inspector**: `fastmcp inspect` for tool verification
4. **Claude Desktop**: End-to-end testing

---

## Resources

- [FastMCP Docs](https://gofastmcp.com)
- [Reclaim API Swagger](https://api.app.reclaim.ai/swagger/reclaim-api-0.1.yml)
- [Existing TypeScript Server](https://github.com/jj3ny/reclaim-mcp-server)
- [GitLab Python Guide](https://docs.gitlab.com/development/python_guide/)
- GitLab Duo-Ready project standards

---

## Roadmap

### v0.8.0 (Current) ✅

**Theme**: Distribution & Profiles

- [x] Tool profiles (minimal=20, standard=32, full=40)
- [x] Docker distribution (non-root, multi-stage build)
- [x] Python 3.12 upgrade
- [x] Multi-registry publishing (PyPI, DockerHub, GitLab)
- [x] OIDC Trusted Publishing for PyPI
- [x] Trivy container scanning
- [x] CI workflow optimization (`$CI_COMMIT_REF_PROTECTED`)

### v0.9.0 (Next)

**Theme**: Discoverability via MCP Registries

**Prerequisites** (one-time setup):
- GitHub mirror: `github.com/universalamateur/reclaim-mcp-server`
- GitLab Push Mirror configuration
- Smithery.ai account (GitHub OAuth)
- mcp-publisher CLI

**Files to add**:
- `smithery.yaml` - Smithery.ai deployment config
- `server.json` - MCP Registry definition
- Update `Dockerfile` - MCP namespace labels
- Update `README.md` - MCP marker + badges

**Registries**:
- Smithery.ai (https://smithery.ai/server/reclaim-mcp-server)
- MCP Registry (https://registry.modelcontextprotocol.io/)
- Glama (auto-syncs from MCP Registry)

### v0.10.0 (Planned)

**Theme**: Cross-Architecture Support

- Multi-platform Docker builds (linux/amd64 + linux/arm64)
- buildx setup in CI
- Manifest list for multi-arch support

### v1.0.0+ (Future)

- MCP Resources (`reclaim://today`, `reclaim://tasks/active`)
- Additional Reclaim API coverage
- OAuth flow for API key setup

---

## Known Limitations

| Issue | Description |
|-------|-------------|
| Team analytics | Plan-gated (removed in v0.7.1) |
| `restart_task` | API returns ARCHIVED status - unclear behavior |
| Multi-platform | Docker builds single-arch only until v0.10.0 |
| `pin_event` / `unpin_event` | Upstream API returns HTTP 500 (removed in v0.8.0) |
| `HOURS_DEFENDED` / `FOCUS_WORK_BALANCE` | V3 API returns 400 (removed in v0.8.0) |
