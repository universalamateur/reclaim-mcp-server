# Tool Reference

Complete reference for all 40 tools available in the Reclaim MCP Server.

## Tool Profiles

Control which tools are exposed using `RECLAIM_TOOL_PROFILE`:

| Profile | Tools | Description |
|---------|-------|-------------|
| `minimal` | 20 | Core tasks + habits basics |
| `standard` | 32 | Core productivity (no niche tools) |
| `full` | 40 | All tools (default) |

---

## Tasks (12 tools)

| Tool | Profile | Description |
|------|---------|-------------|
| `list_tasks` | minimal | List active tasks (excludes completed by default) |
| `list_completed_tasks` | minimal | List completed and archived tasks |
| `get_task` | minimal | Get a single task by ID |
| `create_task` | minimal | Create new task for auto-scheduling |
| `update_task` | minimal | Update existing task properties |
| `mark_task_complete` | minimal | Mark task as complete |
| `delete_task` | minimal | Delete a task |
| `add_time_to_task` | standard | Log time spent on task (uses planner API) |
| `start_task` | standard | Start working on task (timer) |
| `stop_task` | standard | Stop working on task |
| `prioritize_task` | standard | Elevate task priority |
| `restart_task` | standard | Restart a completed task |

---

## Calendar Events (5 tools)

| Tool | Profile | Description |
|------|---------|-------------|
| `list_events` | minimal | List calendar events within a time range |
| `list_personal_events` | minimal | List Reclaim-managed events (tasks, habits, focus) |
| `get_event` | minimal | Get single event by calendar ID and event ID |
| `set_event_rsvp` | full | Set RSVP status for event |
| `move_event` | full | Reschedule event to new time |

---

## Smart Habits (14 tools)

| Tool | Profile | Description |
|------|---------|-------------|
| `list_habits` | minimal | List all smart habits |
| `get_habit` | minimal | Get a single habit by lineage ID |
| `create_habit` | minimal | Create new smart habit for auto-scheduling |
| `update_habit` | minimal | Update habit properties |
| `delete_habit` | minimal | Delete a habit |
| `mark_habit_done` | minimal | Mark a habit instance as done |
| `skip_habit` | minimal | Skip a habit instance |
| `enable_habit` | standard | Enable a disabled habit |
| `disable_habit` | standard | Disable a habit without deleting |
| `lock_habit_instance` | full | Lock habit instance to prevent rescheduling |
| `unlock_habit_instance` | full | Unlock habit instance to allow rescheduling |
| `start_habit` | full | Start a habit session now |
| `stop_habit` | full | Stop a running habit session |
| `convert_event_to_habit` | full | Convert calendar event to habit |

---

## Analytics (2 tools)

| Tool | Profile | Description |
|------|---------|-------------|
| `get_user_analytics` | minimal | Personal productivity analytics (Pro plan) |
| `get_focus_insights` | standard | Focus time analysis and recommendations (Pro plan) |

**Available metrics**:
- `DURATION_BY_CATEGORY` - Time breakdown by category
- `DURATION_BY_DATE_BY_CATEGORY` - Daily time breakdown by category

---

## Focus Time (5 tools)

| Tool | Profile | Description |
|------|---------|-------------|
| `get_focus_settings` | standard | Get current focus time settings |
| `update_focus_settings` | standard | Update focus duration and defense level |
| `lock_focus_block` | standard | Lock focus block to prevent rescheduling |
| `unlock_focus_block` | standard | Unlock focus block |
| `reschedule_focus_block` | standard | Move focus block to new time |

---

## Utility (2 tools)

| Tool | Profile | Description |
|------|---------|-------------|
| `health_check` | minimal | Server health check with version info |
| `verify_connection` | minimal | Verify API connection by fetching current user |

---

## Profile Details

### Minimal Profile (20 tools)

Core task and habit management for basic productivity:

- **Tasks**: list, list_completed, get, create, update, delete, complete
- **Habits**: list, get, create, update, delete, mark_done, skip
- **Events**: list, list_personal, get
- **Analytics**: get_user_analytics
- **System**: health_check, verify_connection

### Standard Profile (32 tools)

Adds workflow and focus management:

- Everything in minimal, plus:
- **Task workflow**: add_time, start, stop, prioritize, restart
- **Habit workflow**: enable, disable
- **Focus**: settings, lock, unlock, reschedule
- **Analytics**: focus_insights

### Full Profile (40 tools)

All available tools:

- Everything in standard, plus:
- **Event management**: set_rsvp, move
- **Habit advanced**: lock/unlock instances, start/stop sessions, convert_event_to_habit
