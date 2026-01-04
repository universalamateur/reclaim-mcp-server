# Contributing to reclaim-mcp-server

Thank you for your interest in contributing! We welcome contributions of all kinds: bug reports, feature requests, documentation improvements, and code changes.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming environment for everyone.

## How to Contribute

### Reporting Bugs

Found a bug? Please [open an issue](https://gitlab.com/universalamateur1/reclaim-mcp-server/-/issues/new?issuable_template=Bug) using our bug template. Include:
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, OS)

### Suggesting Features

Have an idea? [Open a feature request](https://gitlab.com/universalamateur1/reclaim-mcp-server/-/issues/new?issuable_template=Feature) with:
- Clear description of the feature
- Use case / motivation
- Any implementation ideas

## Development Setup

### Prerequisites

- Python 3.12+
- Poetry 2.x

### Installation

```bash
# Clone the repository
git clone git@gitlab.com:universalamateur1/reclaim-mcp-server.git
cd reclaim-mcp-server

# Install dependencies
poetry install

# Set up environment variables
export RECLAIM_API_KEY="your_api_key_here"
```

## Code Style

This project uses automated formatting and linting:

- **Black**: Code formatting (120 line length)
- **isort**: Import sorting (Black profile)
- **flake8**: Linting
- **mypy**: Type checking (strict mode)

### Running Checks Locally

```bash
# Format code
poetry run black src tests
poetry run isort src tests

# Check formatting
poetry run black --check src tests
poetry run isort --check-only src tests

# Lint
poetry run flake8 src tests

# Type check
poetry run mypy src
```

## Testing

Tests use pytest with pytest-asyncio for async support.

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/reclaim_mcp --cov-report=term

# Run specific test file
poetry run pytest tests/test_client.py -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_create_task_with_valid_data`
- Mock external API calls using `monkeypatch`
- Test both success and error paths

## Merge Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all checks pass locally
4. Create a merge request using the default template
5. Address review feedback
6. Squash and merge when approved

## Commit Messages

Use conventional commit format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Example: `feat: add task priority support`
