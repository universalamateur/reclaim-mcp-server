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
