"""Shared utilities for Reclaim MCP tools."""

from pydantic import ValidationError


def format_validation_errors(e: ValidationError) -> str:
    """Format Pydantic validation errors into a user-friendly message."""
    errors = "; ".join(err["msg"] for err in e.errors())
    return f"Invalid input: {errors}"
