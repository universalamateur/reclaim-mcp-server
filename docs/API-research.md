# Reclaim.ai API Research Report

> Combined findings from reverse engineering analysis and community implementation review.

## Executive Summary

The Reclaim.ai API has significant **undocumented capabilities** beyond the official Swagger specification. The official spec at `api.app.reclaim.ai/swagger/reclaim-api-0.1.yml` is effectively deprecated—community SDKs are reverse-engineered from the web app. A "Shadow API" powers the platform's real functionality.

| Category | REST API | Webhooks | Notes |
|----------|----------|----------|-------|
| Tasks | ✅ Full CRUD + Planner | ❌ | Primary integration point |
| Habits | ✅ Full CRUD | ❌ | Discovered via reverse engineering |
| Events | ✅ Read + Planner | ❌ | Calendar sync operations |
| Scheduling Links | ❌ None | ✅ Full | Webhook-only for meetings |
| Buffer Time | ❌ None | ❌ | Configured via TimeSchemes |
| Analytics | ✅ Read | ❌ | Premium plans only |
| Focus Time | ✅ Read + Update | ❌ | Settings management |
| SCIM | ✅ Full | ❌ | Enterprise only |

**Base URL**: `https://api.app.reclaim.ai`
**Auth**: `Authorization: Bearer {API_KEY}`
**Rate Limit**: 100 requests/minute

---

## Key Architectural Insight: Agentic Scheduling

Reclaim.ai uses **constraint-based scheduling**, not traditional calendar CRUD. You don't specify "create event at 2 PM"—you specify constraints (duration, deadline, priority) and the AI solver allocates time slots dynamically.

**Implication**: "One-off Events" are **Tasks** with constraints that force single-block scheduling:
- Set `minChunkSize` = `timeChunksRequired` to prevent splitting
- The AI "hydrates" the Task into calendar events

---

## Discovered Endpoints

### 1. Planner API (State Mutation)

The `api/planner` namespace is the **control plane** for the scheduling engine. These endpoints trigger solver recalculation, not simple database updates.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/planner/prioritize/task/{id}` | Elevate priority, trigger reschedule |
| POST | `/api/planner/start/task/{id}` | Start timer, lock calendar slot |
| POST | `/api/planner/stop/task/{id}` | Stop timer, release future slots |
| POST | `/api/planner/done/task/{id}` | Mark complete, remove constraint |
| POST | `/api/planner/add-time/task/{id}` | Add duration, find additional slots |
| POST | `/api/planner/log-work/task/{id}` | Log time retroactively (analytics) |
| POST | `/api/planner/unarchive/task/{id}` | Restore to active scheduling |
| POST | `/api/planner/clear-exceptions/task/{id}` | Revert to AI-driven scheduling |

### 2. Tasks API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/tasks` | List tasks (filter: `status`, `planner`) |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/{id}` | Get task details |
| PATCH | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/reindex-by-due` | Trigger AI re-sort by due dates |

**Create Task Payload**:
```json
{
  "title": "Complete report",
  "timeChunksRequired": 120,
  "minChunkSize": 30,
  "maxChunkSize": 60,
  "due": "2026-01-15T17:00:00Z",
  "priority": "P2",
  "snoozeUntil": "2026-01-10T09:00:00Z",
  "onDeck": true,
  "alwaysPrivate": false,
  "eventColor": "#FF5733"
}
```

### 3. Habits API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/habits` | List all habits |
| POST | `/api/habits` | Create habit |
| GET | `/api/habits/{lineageId}` | Get habit details |
| PATCH | `/api/habits/{lineageId}` | Update habit |
| DELETE | `/api/habits/{lineageId}` | Delete habit |

**Habit Planner Operations**:
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/habits/planner/{lineageId}/start` | Start session now |
| POST | `/api/habits/planner/{lineageId}/stop` | Stop running session |
| POST | `/api/habits/planner/{lineageId}/done` | Mark instance done |
| POST | `/api/habits/planner/{lineageId}/skip` | Skip instance |

### 4. Events API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/planner/events/list` | List calendar events (date range) |
| GET | `/api/planner/events/personal` | List Reclaim-managed events |
| GET | `/api/planner/events/{calendarId}/{eventId}` | Get event details |

**Event Planner Operations** (Reclaim-managed events only):
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/planner/{calendarId}/{eventId}/pin` | Lock to current time |
| POST | `/api/planner/{calendarId}/{eventId}/unpin` | Allow rescheduling |
| POST | `/api/planner/{calendarId}/{eventId}/reschedule` | Move to new time |
| POST | `/api/planner/{calendarId}/{eventId}/rsvp` | Set RSVP status |

### 5. Analytics API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/analytics/user/V3` | Personal productivity metrics |
| GET | `/api/analytics/focus/insights/V3` | Focus time analysis |

**Query Parameters**: `start`, `end`, `metricName[]`
**Available Metrics**: `DURATION_BY_CATEGORY`, `DURATION_BY_DATE_BY_CATEGORY`

### 6. Focus Time API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/focus-settings/user` | Get focus settings (returns list) |
| PATCH | `/api/focus-settings/user/{id}` | Update focus settings |

### 7. Configuration Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/timeschemes` | Availability rules (working hours, buffers) |
| GET | `/api/users/current` | Current user info |

---

## Scheduling Links (Webhook-Only)

**No REST API exists** for Scheduling Links CRUD. Only outbound webhooks are supported.

### Webhook Events

| Event | Description |
|-------|-------------|
| `SchedulingLink.Meeting.Created` | Meeting booked |
| `SchedulingLink.Meeting.Updated` | Meeting rescheduled |
| `SchedulingLink.Meeting.Cancelled` | Meeting cancelled |

### Webhook Security

- **Header**: `x-reclaim-signature-256`
- **Algorithm**: HMAC-SHA256 with shared secret
- **Replay Protection**: Check `webhook_sent_at` / `event_ts` timestamps (reject if > 5 min old)

### Custom Data Passthrough

Append query params to booking URL: `?data-crm-id=12345`
Data echoed back in webhook `custom_data` field for correlation.

---

## Buffer Time

**No dedicated API**. Buffer time is a derived property from:

1. **TimeScheme policies** (`/api/timeschemes`) - Working hours, availability windows
2. **Scheduling Link configurations** - Per-link buffer settings (UI only)
3. **Hashtag controls** in calendar events:
   - `#needs_travel` - Force travel buffer
   - `#flight` - 2h before, 1h after
   - `#reclaim_free` - No-Meeting Day

---

## Authentication

| Method | Details |
|--------|---------|
| API Key | Generate at `app.reclaim.ai/settings/developer` |
| Format | UUID: `877dfde9-1676-4ae2-80d5-67c9c0a970e1` |
| Header | `Authorization: Bearer {API_KEY}` |
| Expiration | Configurable, including "Forever" |

**Security Note**: "Forever" tokens are high-risk. Treat as critical secrets, implement rotation.

---

## Enterprise: SCIM API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/scim/v2/Users` | GET/POST/PATCH/DELETE | User provisioning |

**Base URL**: `https://api.app.reclaim.ai/scim/v2`
**Availability**: Enterprise plan, Google Calendar only

---

## API Quirks

| Quirk | Details |
|-------|---------|
| `idealTime` format | Must include seconds: `HH:MM:SS` not `HH:MM` |
| `defenseAggression` | Values: `DEFAULT`, `NONE`, `LOW`, `MEDIUM`, `HIGH`, `MAX` |
| `timePolicyType` | Values: `WORK`, `PERSONAL`, `MEETING`, `ONE_OFF` |
| Habit scheduling | Async—newly created habits may not have instances immediately |
| Event IDs | Habit `eventKey` ≠ `eventId` from personal events |

---

## Sources

- [Reclaim.ai Help Center](https://help.reclaim.ai)
- [reclaim-sdk (Python)](https://github.com/llabusch93/reclaim-sdk) - Reverse-engineered
- [Raycast Extension](https://www.raycast.com/reclaim-ai/reclaim-ai)
- [reclaim-ai Rust Crate](https://crates.io/crates/reclaim-ai)
- [n8n Reclaim Node](https://n8n.io)
- Browser DevTools network analysis

---

*Last updated: 2026-01-02*
