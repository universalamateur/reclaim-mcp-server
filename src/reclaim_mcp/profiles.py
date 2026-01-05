"""Tool profile definitions for Reclaim MCP Server.

Profiles allow users to limit which tools are exposed based on their needs:
- minimal: Core tasks + habits basics (20 tools)
- standard: Core productivity without niche tools (32 tools)
- full: All tools (40 tools, default)
"""

from typing import Literal

ProfileName = Literal["minimal", "standard", "full"]

# Minimal profile: Core tasks + habits basics (20 tools)
MINIMAL_TOOLS: set[str] = {
    # System (2)
    "health_check",
    "verify_connection",
    # Tasks (7)
    "list_tasks",
    "create_task",
    "update_task",
    "mark_task_complete",
    "delete_task",
    "get_task",
    "list_completed_tasks",
    # Habits (6)
    "list_habits",
    "create_habit",
    "update_habit",
    "delete_habit",
    "mark_habit_done",
    "skip_habit",
    # Events (3)
    "list_events",
    "list_personal_events",
    "get_event",
    # Focus (1)
    "get_focus_settings",
    # Analytics (1)
    "get_user_analytics",
}

# Standard profile: Adds workflow tools (32 tools)
STANDARD_TOOLS: set[str] = MINIMAL_TOOLS | {
    # Tasks workflow (5)
    "add_time_to_task",
    "start_task",
    "stop_task",
    "prioritize_task",
    "restart_task",
    # Habits workflow (2)
    "enable_habit",
    "disable_habit",
    # Focus management (4)
    "update_focus_settings",
    "lock_focus_block",
    "unlock_focus_block",
    "reschedule_focus_block",
    # Analytics (1)
    "get_focus_insights",
}

# Full profile: All tools (40 tools)
FULL_TOOLS: set[str] = STANDARD_TOOLS | {
    # Events advanced (2)
    "set_event_rsvp",
    "move_event",
    # Habits advanced (5)
    "lock_habit_instance",
    "unlock_habit_instance",
    "start_habit",
    "stop_habit",
    "convert_event_to_habit",
    # Habit extra (1) - get_habit wasn't in minimal
    "get_habit",
}

PROFILES: dict[str, set[str]] = {
    "minimal": MINIMAL_TOOLS,
    "standard": STANDARD_TOOLS,
    "full": FULL_TOOLS,
}


def get_enabled_tools(profile: str = "full") -> set[str]:
    """Get the set of enabled tools for a given profile.

    Args:
        profile: Profile name (minimal, standard, full). Defaults to full.

    Returns:
        Set of tool names that should be enabled.
        Falls back to full profile for invalid profile names.
    """
    return PROFILES.get(profile.lower(), FULL_TOOLS)


def is_tool_enabled(tool_name: str, profile: str = "full") -> bool:
    """Check if a tool is enabled for the given profile.

    Args:
        tool_name: Name of the tool to check.
        profile: Profile name (minimal, standard, full). Defaults to full.

    Returns:
        True if the tool is enabled for the profile.
    """
    return tool_name in get_enabled_tools(profile)


def get_profile_info() -> dict[str, int]:
    """Get tool counts for each profile.

    Returns:
        Dict mapping profile name to tool count.
    """
    return {name: len(tools) for name, tools in PROFILES.items()}
