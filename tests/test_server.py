"""Tests for the MCP server."""

from reclaim_mcp import __version__


def test_version() -> None:
    """Test that version is defined."""
    assert __version__ == "0.3.0"
