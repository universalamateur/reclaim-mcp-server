# Release Process

This document describes the release process for reclaim-mcp-server.

## Overview

Releases are published to multiple registries via GitLab CI/CD:

| Registry | URL | Auth Method |
|----------|-----|-------------|
| **PyPI** | https://pypi.org/project/reclaim-mcp-server/ | OIDC Trusted Publishing |
| **TestPyPI** | https://test.pypi.org/project/reclaim-mcp-server/ | OIDC Trusted Publishing |
| **GitLab Package Registry** | Project → Packages | `$CI_JOB_TOKEN` (automatic) |
| **GitLab Container Registry** | Project → Container Registry | `$CI_REGISTRY_*` (automatic) |
| **DockerHub** | https://hub.docker.com/r/universalamateur/reclaim-mcp-server | Access token |

## Pipeline Architecture

```
lint → test → security → build → publish → release

                    build-package ─────────────────────────────────┐
                          │                                        │
                    build-docker                                   │
                          │                                        │
    ┌─────────────────────┼─────────────────────────┐              │
    ↓                     ↓                         ↓              │
publish-gitlab    publish-testpypi          publish-gitlab    create-release
  -package          (manual)                 -container            ↑
                      │                           │                │
                      ↓                           ↓                │
                publish-pypi              publish-dockerhub ───────┘
                 (manual)                   (manual)
```

**Key Design Decisions:**
- All publish jobs are **manual** to prevent accidental releases
- TestPyPI → PyPI flow for pre-release validation
- OIDC Trusted Publishing (no API token secrets needed for PyPI)
- GitLab Environments track deployments

## Pre-Release Checklist

Before creating a release:

1. **Update version** in all locations:
   ```
   pyproject.toml        → [project] version
   pyproject.toml        → [tool.poetry] version
   src/reclaim_mcp/__init__.py → __version__
   tests/test_server.py  → version assertion
   ```

2. **Update CHANGELOG.md** with release notes

3. **Run full test suite**:
   ```bash
   poetry run pytest
   poetry run black --check src tests
   poetry run isort --check-only src tests
   poetry run flake8 src tests
   poetry run mypy src
   ```

4. **Update poetry.lock**:
   ```bash
   poetry lock
   ```

5. **Commit and push to main**:
   ```bash
   git add -A
   git commit -m "chore: prepare release vX.Y.Z"
   git push origin main
   ```

## Creating a Release

### Step 1: Create and Push Tag

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

This triggers the CI pipeline with all publish jobs available.

### Step 2: Trigger Publish Jobs (GitLab UI)

Navigate to **CI/CD → Pipelines** and manually trigger jobs in order:

1. **`publish-testpypi`** - Validate on TestPyPI first
   ```bash
   # Test installation from TestPyPI
   pip install -i https://test.pypi.org/simple/ reclaim-mcp-server==X.Y.Z
   ```

2. **`publish-pypi`** - Production PyPI release

3. **`publish-gitlab-package`** - GitLab Package Registry

4. **`publish-gitlab-container`** - GitLab Container Registry

5. **`publish-dockerhub`** - DockerHub

6. **`create-release`** - GitLab Release with asset links

### Step 3: Verify Release

Check all registries:

```bash
# PyPI
pip install reclaim-mcp-server==X.Y.Z

# TestPyPI
pip install -i https://test.pypi.org/simple/ reclaim-mcp-server==X.Y.Z

# DockerHub
docker pull universalamateur/reclaim-mcp-server:vX.Y.Z

# GitLab Container Registry
docker pull registry.gitlab.com/universalamateur1/reclaim-mcp-server:vX.Y.Z
```

## CI/CD Variables

### Required Variables (Settings → CI/CD → Variables)

| Variable | Type | Description |
|----------|------|-------------|
| `DOCKERHUB_USERNAME` | Protected | DockerHub account username |
| `DOCKERHUB_TOKEN` | Protected, Masked | DockerHub access token |

### Automatic Variables (No Configuration Needed)

| Variable | Source |
|----------|--------|
| `CI_JOB_TOKEN` | GitLab CI (auto-provided) |
| `CI_REGISTRY_*` | GitLab CI (auto-provided) |
| `PYPI_ID_TOKEN` | OIDC (declared in `.gitlab-ci.yml`) |

## OIDC Trusted Publishing Setup

PyPI and TestPyPI use OIDC Trusted Publishing instead of API tokens.

### One-Time Setup (PyPI)

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new pending publisher:
   - **PyPI Project Name**: `reclaim-mcp-server`
   - **Owner**: `universalamateur1`
   - **Repository**: `reclaim-mcp-server`
   - **Workflow name**: `.gitlab-ci.yml`
   - **Environment**: `release`

### One-Time Setup (TestPyPI)

1. Go to https://test.pypi.org/manage/account/publishing/
2. Add a new pending publisher with same details, except:
   - **Environment**: `release-test`

## GitLab Environments

The pipeline uses GitLab Environments for tracking:

| Environment | URL | Purpose |
|-------------|-----|---------|
| `release-test` | https://test.pypi.org/project/reclaim-mcp-server/ | TestPyPI tracking |
| `release` | https://pypi.org/project/reclaim-mcp-server/ | Production PyPI |
| `docker` | https://hub.docker.com/r/universalamateur/reclaim-mcp-server | DockerHub tracking |

## Troubleshooting

### OIDC Token Exchange Failed

If PyPI/TestPyPI publish fails with "Token exchange failed":

1. Verify OIDC publisher is configured on PyPI/TestPyPI
2. Check environment name matches (`release` or `release-test`)
3. Verify repository path matches exactly

### DockerHub Authentication Failed

1. Verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` variables are set
2. Check token hasn't expired (DockerHub → Security → Access Tokens)
3. Ensure variables are marked as "Protected" if publishing from protected branches

### Container Scan Failures

Trivy container scanning is set to `allow_failure: true`. Critical vulnerabilities will be reported but won't block the pipeline. Review and address as needed.

## Security Notes

- **No PyPI tokens stored** - OIDC Trusted Publishing eliminates token management
- **DockerHub token only** - Single secret to manage
- **Manual triggers** - All publish jobs require explicit action
- **Protected variables** - Secrets only available on protected branches/tags
