"""Tests for the TTL cache utility."""

import time

import pytest

from reclaim_mcp.cache import get_cache_stats, invalidate_cache, ttl_cache


class TestTTLCache:
    """Tests for ttl_cache decorator."""

    @pytest.mark.asyncio
    async def test_cache_hit(self) -> None:
        """Test that cached values are returned on subsequent calls."""
        call_count = 0

        @ttl_cache(ttl=60)
        async def cached_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call - should execute function
        result1 = await cached_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call - should return cached value
        result2 = await cached_function(5)
        assert result2 == 10
        assert call_count == 1  # Still 1, cache hit

        # Different argument - should execute function
        result3 = await cached_function(10)
        assert result3 == 20
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cache_miss_on_different_args(self) -> None:
        """Test that different arguments result in cache miss."""
        call_count = 0

        @ttl_cache(ttl=60)
        async def cached_function(x: int, y: int = 0) -> int:
            nonlocal call_count
            call_count += 1
            return x + y

        await cached_function(1, 2)
        assert call_count == 1

        await cached_function(1, 3)  # Different y
        assert call_count == 2

        await cached_function(1, 2)  # Same as first call
        assert call_count == 2  # Cache hit

    @pytest.mark.asyncio
    async def test_error_strings_not_cached(self) -> None:
        """Test that error strings are not cached."""
        call_count = 0

        @ttl_cache(ttl=60)
        async def cached_function(fail: bool) -> str:
            nonlocal call_count
            call_count += 1
            if fail:
                return "Error: Something went wrong"
            return "Success"

        # Error should not be cached
        result1 = await cached_function(True)
        assert result1.startswith("Error")
        assert call_count == 1

        # Called again, should still execute (not cached)
        result2 = await cached_function(True)
        assert result2.startswith("Error")
        assert call_count == 2

        # Success should be cached
        result3 = await cached_function(False)
        assert result3 == "Success"
        assert call_count == 3

        result4 = await cached_function(False)
        assert result4 == "Success"
        assert call_count == 3  # Cache hit


class TestInvalidateCache:
    """Tests for invalidate_cache function."""

    @pytest.mark.asyncio
    async def test_invalidate_by_prefix(self) -> None:
        """Test invalidating cache by prefix."""
        call_count_a = 0
        call_count_b = 0

        @ttl_cache(ttl=60)
        async def func_a() -> str:
            nonlocal call_count_a
            call_count_a += 1
            return "a"

        @ttl_cache(ttl=60)
        async def func_b() -> str:
            nonlocal call_count_b
            call_count_b += 1
            return "b"

        # Populate cache
        await func_a()
        await func_b()
        assert call_count_a == 1
        assert call_count_b == 1

        # Verify cache hit
        await func_a()
        await func_b()
        assert call_count_a == 1
        assert call_count_b == 1

        # Invalidate only func_a
        invalidate_cache("func_a")

        # func_a should be cache miss, func_b still cached
        await func_a()
        await func_b()
        assert call_count_a == 2
        assert call_count_b == 1

    @pytest.mark.asyncio
    async def test_invalidate_all(self) -> None:
        """Test invalidating entire cache."""
        call_count = 0

        @ttl_cache(ttl=60)
        async def cached_function() -> str:
            nonlocal call_count
            call_count += 1
            return "result"

        # Populate and verify cache
        await cached_function()
        await cached_function()
        assert call_count == 1

        # Clear all cache
        invalidate_cache()

        # Should be cache miss
        await cached_function()
        assert call_count == 2


class TestCacheStats:
    """Tests for get_cache_stats function."""

    def test_cache_stats(self) -> None:
        """Test cache statistics are returned correctly."""
        # Clear cache first
        invalidate_cache()

        stats = get_cache_stats()
        assert "total_entries" in stats
        assert "valid_entries" in stats
        assert "expired_entries" in stats
        assert stats["total_entries"] == 0
