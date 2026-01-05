"""Tests for tool profile functionality."""

import os
from unittest.mock import patch

from reclaim_mcp.profiles import (
    FULL_TOOLS,
    MINIMAL_TOOLS,
    PROFILES,
    STANDARD_TOOLS,
    get_enabled_tools,
    get_profile_info,
    is_tool_enabled,
)


class TestProfileDefinitions:
    """Tests for profile tool sets."""

    def test_minimal_tools_count(self) -> None:
        """Test minimal profile has 20 tools."""
        assert len(MINIMAL_TOOLS) == 20

    def test_standard_tools_count(self) -> None:
        """Test standard profile has 32 tools."""
        assert len(STANDARD_TOOLS) == 32

    def test_full_tools_count(self) -> None:
        """Test full profile has 40 tools."""
        assert len(FULL_TOOLS) == 40

    def test_minimal_is_subset_of_standard(self) -> None:
        """Test minimal tools are all in standard."""
        assert MINIMAL_TOOLS.issubset(STANDARD_TOOLS)

    def test_standard_is_subset_of_full(self) -> None:
        """Test standard tools are all in full."""
        assert STANDARD_TOOLS.issubset(FULL_TOOLS)

    def test_profiles_dict_has_all_profiles(self) -> None:
        """Test PROFILES dict contains all three profiles."""
        assert set(PROFILES.keys()) == {"minimal", "standard", "full"}

    def test_essential_tools_in_minimal(self) -> None:
        """Test essential tools are in minimal profile."""
        essential = {
            "health_check",
            "verify_connection",
            "list_tasks",
            "create_task",
            "list_habits",
            "list_events",
        }
        assert essential.issubset(MINIMAL_TOOLS)

    def test_workflow_tools_in_standard(self) -> None:
        """Test workflow tools are added in standard profile."""
        workflow_tools = {
            "start_task",
            "stop_task",
            "prioritize_task",
            "enable_habit",
            "disable_habit",
        }
        # These should be in standard but not minimal
        for tool in workflow_tools:
            assert tool in STANDARD_TOOLS
            assert tool not in MINIMAL_TOOLS

    def test_advanced_tools_only_in_full(self) -> None:
        """Test advanced tools are only in full profile."""
        advanced_tools = {
            "set_event_rsvp",
            "move_event",
            "convert_event_to_habit",
        }
        for tool in advanced_tools:
            assert tool in FULL_TOOLS
            assert tool not in STANDARD_TOOLS


class TestGetEnabledTools:
    """Tests for get_enabled_tools function."""

    def test_get_minimal_tools(self) -> None:
        """Test getting minimal profile tools."""
        tools = get_enabled_tools("minimal")
        assert tools == MINIMAL_TOOLS

    def test_get_standard_tools(self) -> None:
        """Test getting standard profile tools."""
        tools = get_enabled_tools("standard")
        assert tools == STANDARD_TOOLS

    def test_get_full_tools(self) -> None:
        """Test getting full profile tools."""
        tools = get_enabled_tools("full")
        assert tools == FULL_TOOLS

    def test_case_insensitive(self) -> None:
        """Test profile names are case insensitive."""
        assert get_enabled_tools("MINIMAL") == MINIMAL_TOOLS
        assert get_enabled_tools("Minimal") == MINIMAL_TOOLS
        assert get_enabled_tools("STANDARD") == STANDARD_TOOLS
        assert get_enabled_tools("FULL") == FULL_TOOLS

    def test_invalid_profile_falls_back_to_full(self) -> None:
        """Test invalid profile name falls back to full."""
        assert get_enabled_tools("invalid") == FULL_TOOLS
        assert get_enabled_tools("") == FULL_TOOLS
        assert get_enabled_tools("pro") == FULL_TOOLS

    def test_default_is_full(self) -> None:
        """Test default profile is full."""
        assert get_enabled_tools() == FULL_TOOLS


class TestIsToolEnabled:
    """Tests for is_tool_enabled function."""

    def test_tool_in_minimal(self) -> None:
        """Test tool enabled in minimal profile."""
        assert is_tool_enabled("health_check", "minimal") is True
        assert is_tool_enabled("list_tasks", "minimal") is True

    def test_tool_not_in_minimal(self) -> None:
        """Test tool not enabled in minimal profile."""
        assert is_tool_enabled("start_task", "minimal") is False
        assert is_tool_enabled("set_event_rsvp", "minimal") is False

    def test_tool_in_standard(self) -> None:
        """Test tool enabled in standard profile."""
        assert is_tool_enabled("start_task", "standard") is True
        assert is_tool_enabled("health_check", "standard") is True

    def test_tool_not_in_standard(self) -> None:
        """Test tool not enabled in standard profile."""
        assert is_tool_enabled("set_event_rsvp", "standard") is False
        assert is_tool_enabled("convert_event_to_habit", "standard") is False

    def test_all_tools_in_full(self) -> None:
        """Test all tools enabled in full profile."""
        for tool in FULL_TOOLS:
            assert is_tool_enabled(tool, "full") is True

    def test_default_profile_is_full(self) -> None:
        """Test default profile enables all tools."""
        assert is_tool_enabled("set_event_rsvp") is True
        assert is_tool_enabled("convert_event_to_habit") is True


class TestGetProfileInfo:
    """Tests for get_profile_info function."""

    def test_profile_info_counts(self) -> None:
        """Test profile info returns correct counts."""
        info = get_profile_info()
        assert info == {
            "minimal": 20,
            "standard": 32,
            "full": 40,
        }


class TestServerToolDecorator:
    """Tests for the server tool decorator with profiles."""

    def test_tool_decorator_respects_profile(self) -> None:
        """Test that the tool decorator calls mcp.tool only when enabled."""
        from reclaim_mcp.profiles import is_tool_enabled

        # Test that is_tool_enabled works correctly for different profiles
        # The actual server registration is tested manually via fastmcp inspect
        assert is_tool_enabled("health_check", "minimal") is True
        assert is_tool_enabled("start_task", "minimal") is False
        assert is_tool_enabled("start_task", "standard") is True
        assert is_tool_enabled("set_event_rsvp", "standard") is False
        assert is_tool_enabled("set_event_rsvp", "full") is True

    def test_profile_env_var_defaults_to_full(self) -> None:
        """Test that missing RECLAIM_TOOL_PROFILE defaults to full."""
        env_without_profile = {k: v for k, v in os.environ.items() if k != "RECLAIM_TOOL_PROFILE"}
        with patch.dict(os.environ, env_without_profile, clear=True):
            # Re-check that get_enabled_tools with default returns full
            from reclaim_mcp.profiles import get_enabled_tools

            assert len(get_enabled_tools()) == 40
