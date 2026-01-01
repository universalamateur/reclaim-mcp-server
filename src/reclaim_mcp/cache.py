"""Simple TTL cache for read-only API responses."""

import time
from functools import wraps
from typing import Any, Callable, TypeVar

# Simple in-memory cache with TTL
_cache: dict[str, tuple[float, Any]] = {}

# Default TTL in seconds
DEFAULT_TTL = 60

# Type variable for async functions
F = TypeVar("F", bound=Callable[..., Any])


def ttl_cache(ttl: int = DEFAULT_TTL) -> Callable[[F], F]:
    """Decorator for caching async function results with TTL.

    Args:
        ttl: Time-to-live in seconds (default 60)

    Returns:
        Decorated function with caching.

    Example:
        @ttl_cache(ttl=120)
        async def list_habits() -> list[dict]:
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build cache key from function name and arguments
            cache_key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            now = time.time()

            # Check cache hit
            if cache_key in _cache:
                expires, value = _cache[cache_key]
                if now < expires:
                    return value

            # Cache miss - call function and store result
            result = await func(*args, **kwargs)

            # Only cache successful results (not error strings)
            if not isinstance(result, str) or not result.startswith("Error"):
                _cache[cache_key] = (now + ttl, result)

            return result

        return wrapper  # type: ignore

    return decorator


def invalidate_cache(prefix: str | None = None) -> None:
    """Invalidate cache entries, optionally by prefix.

    Args:
        prefix: If provided, only invalidate entries starting with this prefix.
                If None, clears the entire cache.

    Example:
        invalidate_cache("list_habits")  # Clear habit list cache
        invalidate_cache()  # Clear all cache
    """
    global _cache
    if prefix:
        _cache = {k: v for k, v in _cache.items() if not k.startswith(prefix)}
    else:
        _cache.clear()


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics for debugging.

    Returns:
        Dict with cache size and entry info.
    """
    now = time.time()
    valid_entries = sum(1 for _, (expires, _) in _cache.items() if expires > now)
    return {
        "total_entries": len(_cache),
        "valid_entries": valid_entries,
        "expired_entries": len(_cache) - valid_entries,
    }
