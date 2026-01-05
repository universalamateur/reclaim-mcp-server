# Reclaim.ai API Reference

> Based on analysis of https://api.app.reclaim.ai/swagger/reclaim-api-0.1.yml

## API Specification

The official OpenAPI spec is stored at `docs/reclaim-api-0.1.yml` (29,118 lines).

## Key Findings

### Task Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tasks` | GET | List tasks with status filter |
| `/api/tasks` | POST | Create new task |
| `/api/tasks/{id}` | GET | Get single task |
| `/api/tasks/{taskId}` | PUT | Replace entire task |
| `/api/tasks/{id}` | DELETE | Delete task |

### Planner Action Endpoints (Important!)

These endpoints trigger planner recalculation and are the **correct** way to perform actions:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/planner/log-work/task/{taskId}?minutes=X` | POST | **Log time worked** |
| `/api/planner/add-time/task/{taskId}?minutes=X` | POST | Add time to task |
| `/api/planner/done/task/{taskId}` | POST | Mark task complete |
| `/api/planner/start/task/{taskId}` | POST | Start working on task |
| `/api/planner/stop/task/{taskId}` | POST | Stop working on task |
| `/api/planner/restart/task/{taskId}` | POST | Restart completed task |
| `/api/planner/unarchive/task/{taskId}` | POST | Unarchive task |

### Task Schema

Key fields in the Task object:

```yaml
Task:
  required:
    - id
    - title
    - status
    - timeChunksRequired
    - timeChunksSpent      # READ-ONLY - computed from logged work
    - timeChunksRemaining  # READ-ONLY - computed field
    - minChunkSize
    - maxChunkSize
    - created
    - updated
  properties:
    id: int64
    title: string
    notes: string
    status: TaskStatus (NEW, SCHEDULED, IN_PROGRESS, COMPLETE, CANCELLED, ARCHIVED)
    priority: PriorityLevel (P1, P2, P3, P4)
    timeChunksRequired: int32
    timeChunksSpent: int32      # Computed - use planner endpoints to modify
    timeChunksRemaining: int32  # Computed
    due: datetime (nullable)
    snoozeUntil: datetime (nullable)
    readOnlyFields: string[]    # Dynamic list of read-only fields per task
```

### Time Tracking Behavior

**Important Discovery**: `timeChunksSpent` cannot be set directly via PATCH.

- ❌ `PATCH /api/tasks/{id}` with `{"timeChunksSpent": X}` - Does NOT persist
- ✅ `POST /api/planner/log-work/task/{taskId}?minutes=X` - Correct approach

The API uses dedicated planner endpoints for time tracking because logging work triggers:
1. Recalculation of `timeChunksRemaining`
2. Calendar event adjustments
3. Analytics updates
4. **Auto-completion**: When `timeChunksSpent == timeChunksRequired`, status changes to COMPLETE

### Task Status Values

```yaml
TaskStatus:
  enum:
    - NEW          # Just created, not scheduled
    - SCHEDULED    # Has calendar events planned
    - IN_PROGRESS  # Currently being worked on
    - COMPLETE     # Finished (deprecated, use ARCHIVED)
    - CANCELLED    # Cancelled
    - ARCHIVED     # Completed and archived
```

### Priority Levels

```yaml
PriorityLevel:
  enum:
    - P1  # Critical
    - P2  # High (default)
    - P3  # Medium
    - P4  # Low
```

## Implementation Notes

### Time Chunks

Reclaim uses 15-minute "chunks" internally:
- `timeChunksRequired = duration_minutes / 15`
- Minimum 1 chunk (15 minutes)
- `minChunkSize` and `maxChunkSize` are in minutes (not chunks)

### Creating Tasks

```python
POST /api/tasks
{
    "title": "Task name",
    "timeChunksRequired": 4,      # 1 hour = 4 chunks
    "minChunkSize": 15,           # minutes
    "maxChunkSize": 60,           # minutes
    "eventCategory": "WORK",
    "priority": "P2",
    "due": "2026-01-15T17:00:00Z" # optional
}
```

### Completing Tasks

Use the planner endpoint, not PATCH:
```python
POST /api/planner/done/task/{taskId}
```

This properly transitions status to ARCHIVED and sets the `finished` timestamp.

## MCP Server Tool Mapping

### Task Tools (v0.1.x - v0.6.0)

| MCP Tool | API Endpoint(s) |
|----------|-----------------|
| `list_tasks` | GET /api/tasks |
| `list_completed_tasks` | GET /api/tasks?status=COMPLETE,ARCHIVED |
| `get_task` | GET /api/tasks/{id} |
| `create_task` | POST /api/tasks |
| `update_task` | PATCH /api/tasks/{id} |
| `mark_task_complete` | POST /api/planner/done/task/{id} |
| `delete_task` | DELETE /api/tasks/{id} |
| `add_time_to_task` | POST /api/planner/log-work/task/{id}?minutes=X |
| `start_task` | POST /api/planner/start/task/{id} |
| `stop_task` | POST /api/planner/stop/task/{id} |
| `prioritize_task` | POST /api/planner/prioritize/task/{id} |
| `restart_task` | POST /api/planner/restart/task/{id} |

### Calendar Tools (v0.2.0 - v0.8.0)

| MCP Tool | API Endpoint(s) |
|----------|-----------------|
| `list_events` | GET /api/events?start=X&end=Y |
| `list_personal_events` | GET /api/events/personal |
| `get_event` | GET /api/events/{calendarId}/{eventId} |
| `set_event_rsvp` | PUT /api/planner/event/rsvp/{calendarId}/{eventId} |
| `move_event` | POST /api/planner/event/move/{eventId}?start=X&end=Y |

**v0.8.0 Changes**:
- `pin_event` / `unpin_event`: **REMOVED** - Upstream API returns HTTP 500 for all requests.

**v0.7.4 Breaking Changes**:
- `set_event_rsvp`: Now uses PUT method (was POST), body field is `responseStatus` (was `rsvpStatus`),
  RSVP values use PascalCase (`Accepted`, `Declined`, `TentativelyAccepted`, `NeedsAction`).
  New `send_updates` parameter controls notifications (default: true).
- `move_event`: Removed `calendar_id` parameter. Now uses v1 API endpoint with query params.

### Habit Tools (v0.3.0)

| MCP Tool | API Endpoint(s) |
|----------|-----------------|
| `list_habits` | GET /api/smart-habits |
| `get_habit` | GET /api/smart-habits/{lineageId} |
| `create_habit` | POST /api/smart-habits |
| `update_habit` | PATCH /api/smart-habits/{lineageId} |
| `delete_habit` | DELETE /api/smart-habits/{lineageId} |
| `mark_habit_done` | POST /api/smart-habits/planner/{eventId}/done |
| `skip_habit` | POST /api/smart-habits/planner/{eventId}/skip |

### Event Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/events` | GET | List events with date range and filters |
| `/api/events/personal` | GET | List Reclaim-managed personal events |
| `/api/events/{calendarId}/{eventId}` | GET | Get single event |
| `/api/availability/suggested-times` | POST | Find available time slots |

### Event Schema

Key fields in the Event object:

```yaml
Event:
  properties:
    eventId: string
    calendarId: int64
    title: string
    eventStart: datetime
    eventEnd: datetime
    location: string (nullable)
    description: string (nullable)
    organizer: string (nullable)
    priority: PriorityLevel
    type: EventType (EXTERNAL, RECLAIM_MANAGED, etc.)
    meetingType: MeetingType (nullable)
    rsvpStatus: RsvpStatus (nullable)
    reclaimManaged: boolean
```

### Smart Habits Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/smart-habits` | GET | List all smart habits |
| `/api/smart-habits` | POST | Create new smart habit |
| `/api/smart-habits/{lineageId}` | GET | Get single habit |
| `/api/smart-habits/{lineageId}` | PATCH | Update habit |
| `/api/smart-habits/{lineageId}` | DELETE | Delete habit |
| `/api/smart-habits/planner/{eventId}/done` | POST | Mark habit instance done |
| `/api/smart-habits/planner/{eventId}/skip` | POST | Skip habit instance |

### Smart Habit Schema

```yaml
SmartHabitLineageView:
  properties:
    lineageId: int64          # Primary identifier for the habit
    calendarId: int64
    type: SmartSeriesType
    status: SmartSeriesStatus
    enabled: boolean
    activeSeries: SmartSeriesView

CreateSmartHabitRequest:
  required:
    - title
    - recurrence
    - idealTime
    - durationMinMins
    - enabled
    - organizer
    - eventType
    - defenseAggression
  properties:
    title: string
    idealTime: "HH:MM"        # Partial time format
    durationMinMins: int32
    durationMaxMins: int32
    enabled: boolean
    description: string
    recurrence:
      frequency: DAILY|WEEKLY|MONTHLY|YEARLY
      idealDays: DayOfWeek[]  # For WEEKLY frequency
    organizer:
      timePolicyType: TimePolicyType  # NOT email - controls scheduling windows
    eventType: SmartSeriesEventType
    defenseAggression: DefenseAggression

TimePolicyType:
  enum:
    - WORK       # Use work hours time policy
    - PERSONAL   # Use personal hours time policy
    - MEETING    # Use meeting hours time policy
    - ONE_OFF    # Custom one-off policy
    - INHERITED  # Inherit from parent
    - CUSTOM     # Custom time scheme

SmartSeriesEventType:
  enum:
    - FOCUS
    - SOLO_WORK
    - PERSONAL
    - TEAM_MEETING
    - EXTERNAL_MEETING
    - ONE_ON_ONE

DefenseAggression:
  enum:
    - NONE    # No protection
    - LOW
    - MEDIUM  # Default
    - HIGH
    - MAX     # Maximum protection
```

### Habit ID Types

**Important**: Smart Habits use two different ID types:

- **lineageId**: Identifies the habit series (used for CRUD operations)
- **eventId**: Identifies a specific scheduled instance (used for done/skip actions)

### Analytics Tools (v0.7.0 - v0.7.4)

| MCP Tool | API Endpoint(s) |
|----------|-----------------|
| `get_user_analytics` | GET /api/analytics/user/V3?start=X&end=Y&metricName=Z |
| `get_focus_insights` | GET /api/analytics/focus/insights/V3?start=X&end=Y |

**Note**: Team analytics tools (`get_team_analytics`, `export_team_analytics`) were removed in v0.7.1
as they require a Team plan and caused confusion for users on other plans.

**v0.7.4 Breaking Change**: `get_user_analytics` now requires a single `metric_name` parameter (was optional list).
Valid metric names: `DURATION_BY_CATEGORY`, `DURATION_BY_DATE_BY_CATEGORY`

**v0.8.0 Note**: `HOURS_DEFENDED` and `FOCUS_WORK_BALANCE` metrics were removed as the V3 API returns 400 Bad Request for these.

**Known Limitations**:
- `get_focus_insights`: Historical date ranges may return HTTP 500 errors.
  Use recent date ranges (within last 30-90 days) for reliable results.

### Focus Time Tools (v0.7.0)

| MCP Tool | API Endpoint(s) |
|----------|-----------------|
| `get_focus_settings` | GET /api/focus-settings/user |
| `update_focus_settings` | PATCH /api/focus-settings/user/{id} |
| `lock_focus_block` | POST /api/focus/planner/{calendarId}/{eventId}/lock |
| `unlock_focus_block` | POST /api/focus/planner/{calendarId}/{eventId}/unlock |
| `reschedule_focus_block` | POST /api/focus/planner/{calendarId}/{eventId}/reschedule |

## Input Validation (v0.7.2 - v0.7.4)

The MCP server uses Pydantic models for centralized input validation, providing clear error messages before API calls.

### Task Validation (v0.7.4)

| Field | Rule | Error Message |
|-------|------|---------------|
| `title` | Cannot be empty or whitespace-only | "title cannot be empty or whitespace-only" |
| `duration_minutes` | Must be > 0 | "Input should be greater than 0" |
| `min_chunk_size_minutes` | Must be > 0 | "Input should be greater than 0" |
| `max_chunk_size_minutes` | Must be > 0 (if provided) | "Input should be greater than 0" |
| `min_chunk_size_minutes` vs `max_chunk_size_minutes` | min cannot exceed max | "min_chunk_size_minutes cannot exceed max_chunk_size_minutes" |
| `due_date` | Must be YYYY-MM-DD format | "date must be in YYYY-MM-DD format (e.g., '2026-01-15')" |

### Validated Enums

| Enum | Values | Used In |
|------|--------|---------|
| `HabitFrequency` | DAILY, WEEKLY, MONTHLY, YEARLY | create_habit, update_habit, convert_event_to_habit |
| `DayOfWeek` | MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY | create_habit, update_habit (ideal_days) |
| `EventType` | FOCUS, SOLO_WORK, PERSONAL, MEETING, TEAM_MEETING, EXTERNAL_MEETING, ONE_ON_ONE, EXTERNAL, RECLAIM_MANAGED | create_habit, update_habit |
| `DefenseAggression` | DEFAULT, NONE, LOW, MEDIUM, HIGH, MAX | create_habit, update_habit |
| `TimePolicyType` | WORK, PERSONAL, MEETING | create_habit, update_habit |
| `RsvpStatus` | ACCEPTED (→Accepted), DECLINED (→Declined), TENTATIVE (→TentativelyAccepted), NEEDS_ACTION (→NeedsAction) | set_event_rsvp |

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| `ideal_time` | Must be HH:MM or HH:MM:SS format | "ideal_time must be in HH:MM or HH:MM:SS format (e.g., '09:00')" |
| `ideal_time` | Hour must be 00-23 | "hour must be between 00 and 23" |
| `ideal_time` | Minute must be 00-59 | "minute must be between 00 and 59" |
| `duration_min_mins` | Must be > 0 | "Input should be greater than 0" |
| `duration_max_mins` | Must be > 0 (if provided) | "Input should be greater than 0" |
| `duration_min_mins` vs `duration_max_mins` | min cannot exceed max | "duration_min_mins cannot exceed duration_max_mins" |
| `ideal_days` with DAILY frequency | Cannot use ideal_days with DAILY | "ideal_days cannot be used with DAILY frequency" |
| `start_time` / `end_time` | Must be ISO format | "datetime must be in ISO format (e.g., '2026-01-02T14:00:00Z')" |
| `start_time` vs `end_time` | start must be before end | "start_time must be before end_time" |

### Error Response Format

Validation errors are returned as ToolError with format:
```
Invalid input: <error1>; <error2>; ...
```

Example:
```
Invalid input: ideal_time must be in HH:MM or HH:MM:SS format (e.g., '09:00'); duration_min_mins cannot exceed duration_max_mins
```
