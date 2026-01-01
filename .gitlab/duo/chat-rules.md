# Python Coding Standards

## Language Requirements

- Use Python 3.10+ features
- Type hints are required for all function signatures
- Use `Optional[T]` or `T | None` for nullable types
- Prefer `list[T]` over `List[T]` (Python 3.9+ syntax)

## Formatting

- Black formatter with 120 character line length
- isort with Black profile for import sorting
- Single quotes for strings (except docstrings)

## Docstrings

- Use Google-style docstrings for all public functions
- Include Args, Returns, and Raises sections
- Example:

```python
def create_task(title: str, duration_minutes: int) -> dict:
    """Create a new task in Reclaim.ai.

    Args:
        title: Task title/description
        duration_minutes: Total time needed in minutes

    Returns:
        Created task object as dictionary

    Raises:
        httpx.HTTPStatusError: If API request fails
    """
```

## Async Patterns

- Use `async def` for all API-calling functions
- Use `httpx.AsyncClient` for HTTP requests
- Always use context managers for clients
- Prefer `await` over `asyncio.run()` in library code

## Error Handling

- Catch specific exceptions, never bare `except:`
- Use `raise_for_status()` for HTTP error checking
- Log errors with context before re-raising
- Return meaningful error messages

## Testing

- Use pytest with pytest-asyncio
- Mock external dependencies with monkeypatch
- Test both success and error cases
- Use fixtures for common test data
