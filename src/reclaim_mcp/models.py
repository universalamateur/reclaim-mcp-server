"""Pydantic models for Reclaim.ai API responses."""

import re
from datetime import datetime
from enum import Enum
from typing import Optional, cast

from pydantic import BaseModel, Field, field_validator, model_validator


class TaskStatus(str, Enum):
    """Task status values from Reclaim.ai."""

    NEW = "NEW"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"


class TaskPriority(str, Enum):
    """Task priority values from Reclaim.ai."""

    P1 = "P1"  # Critical
    P2 = "P2"  # High
    P3 = "P3"  # Medium
    P4 = "P4"  # Low


class HabitFrequency(str, Enum):
    """Habit recurrence frequency values."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class DayOfWeek(str, Enum):
    """Days of the week for habit scheduling."""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class EventType(str, Enum):
    """Event type values for habits."""

    FOCUS = "FOCUS"
    SOLO_WORK = "SOLO_WORK"
    PERSONAL = "PERSONAL"
    MEETING = "MEETING"
    TEAM_MEETING = "TEAM_MEETING"
    EXTERNAL_MEETING = "EXTERNAL_MEETING"
    ONE_ON_ONE = "ONE_ON_ONE"
    EXTERNAL = "EXTERNAL"
    RECLAIM_MANAGED = "RECLAIM_MANAGED"


class DefenseAggression(str, Enum):
    """Defense aggression levels for habits."""

    DEFAULT = "DEFAULT"
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    MAX = "MAX"


class TimePolicyType(str, Enum):
    """Time policy types for habits."""

    WORK = "WORK"
    PERSONAL = "PERSONAL"
    MEETING = "MEETING"


class SnoozeOption(str, Enum):
    """Snooze duration presets for tasks."""

    FROM_NOW_15M = "FROM_NOW_15M"
    FROM_NOW_30M = "FROM_NOW_30M"
    FROM_NOW_1H = "FROM_NOW_1H"
    FROM_NOW_2H = "FROM_NOW_2H"
    FROM_NOW_4H = "FROM_NOW_4H"
    TOMORROW = "TOMORROW"
    IN_TWO_DAYS = "IN_TWO_DAYS"
    NEXT_WEEK = "NEXT_WEEK"


class RsvpStatus(str, Enum):
    """RSVP status values for calendar events.

    Values use PascalCase as required by the Reclaim.ai API.
    """

    ACCEPTED = "Accepted"
    DECLINED = "Declined"
    TENTATIVE = "TentativelyAccepted"
    NEEDS_ACTION = "NeedsAction"


class Task(BaseModel):
    """A task from Reclaim.ai."""

    id: int
    title: str
    status: TaskStatus
    time_chunks_required: int = Field(alias="timeChunksRequired")
    time_chunks_spent: int = Field(default=0, alias="timeChunksSpent")
    min_chunk_size: int = Field(alias="minChunkSize")
    max_chunk_size: int = Field(alias="maxChunkSize")
    due: Optional[datetime] = None
    snooze_until: Optional[datetime] = Field(default=None, alias="snoozeUntil")
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    model_config = {"populate_by_name": True}


def _validate_date_format(v: Optional[str]) -> Optional[str]:
    """Validate date is in YYYY-MM-DD format."""
    if v is None:
        return v
    # Accept YYYY-MM-DD format
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
        raise ValueError("date must be in YYYY-MM-DD format (e.g., '2026-01-15')")
    # Validate actual date values
    try:
        year, month, day = int(v[:4]), int(v[5:7]), int(v[8:10])
        datetime(year, month, day)  # This will raise if date is invalid
    except ValueError:
        raise ValueError(f"invalid date: {v}")
    return v


class TaskCreate(BaseModel):
    """Request model for creating a task with validation."""

    title: str
    duration_minutes: int = Field(gt=0)
    min_chunk_size_minutes: int = Field(default=15, gt=0)
    max_chunk_size_minutes: Optional[int] = Field(default=None, gt=0)
    due_date: Optional[str] = None
    snooze_until: Optional[str] = None
    priority: TaskPriority = TaskPriority.P2

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty or whitespace-only."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("title cannot be empty or whitespace-only")
        return stripped

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate due_date is in YYYY-MM-DD format."""
        return _validate_date_format(v)

    @field_validator("max_chunk_size_minutes")
    @classmethod
    def validate_max_chunk_positive(cls, v: Optional[int]) -> Optional[int]:
        """Validate max_chunk_size_minutes is positive when provided."""
        if v is not None and v <= 0:
            raise ValueError("max_chunk_size_minutes must be greater than 0")
        return v

    @model_validator(mode="after")
    def validate_task_constraints(self) -> "TaskCreate":
        """Validate cross-field constraints."""
        if self.max_chunk_size_minutes is not None:
            if self.min_chunk_size_minutes > self.max_chunk_size_minutes:
                raise ValueError("min_chunk_size_minutes cannot exceed max_chunk_size_minutes")
        return self


class TaskUpdate(BaseModel):
    """Request model for updating a task with validation."""

    title: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None)
    status: Optional[TaskStatus] = None
    due_date: Optional[str] = None
    priority: Optional[TaskPriority] = None
    snooze_until: Optional[str] = None
    notes: Optional[str] = None
    min_chunk_size_minutes: Optional[int] = Field(default=None)
    max_chunk_size_minutes: Optional[int] = Field(default=None)

    @field_validator("duration_minutes", "min_chunk_size_minutes", "max_chunk_size_minutes")
    @classmethod
    def validate_positive_int(cls, v: Optional[int]) -> Optional[int]:
        """Validate numeric fields are positive when provided."""
        if v is not None and v <= 0:
            raise ValueError("value must be greater than 0")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty or whitespace-only if provided."""
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("title cannot be empty or whitespace-only")
        return stripped

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate due_date is in YYYY-MM-DD format."""
        return _validate_date_format(v)

    @model_validator(mode="after")
    def validate_update_constraints(self) -> "TaskUpdate":
        """Validate cross-field constraints."""
        if self.min_chunk_size_minutes is not None and self.max_chunk_size_minutes is not None:
            if self.min_chunk_size_minutes > self.max_chunk_size_minutes:
                raise ValueError("min_chunk_size_minutes cannot exceed max_chunk_size_minutes")
        return self


class TaskSnooze(BaseModel):
    """Validation model for snoozing a task."""

    task_id: int = Field(gt=0)
    snooze_option: SnoozeOption


class PlanWork(BaseModel):
    """Validation model for scheduling task work at a specific time."""

    task_id: int = Field(gt=0)
    date_time: str
    duration_minutes: int = Field(gt=0)

    @field_validator("date_time")
    @classmethod
    def validate_datetime_format(cls, v: str) -> str:
        """Validate date_time is in ISO format."""
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
        if not re.match(iso_pattern, v):
            raise ValueError("date_time must be in ISO format (e.g., '2026-01-02T14:00:00Z')")
        return v


# --- Habit Validation Models ---


class HabitCreate(BaseModel):
    """Validation model for creating a habit."""

    title: str
    ideal_time: str
    duration_min_mins: int = Field(gt=0)
    duration_max_mins: Optional[int] = Field(default=None)
    frequency: HabitFrequency = HabitFrequency.WEEKLY
    ideal_days: Optional[list[DayOfWeek]] = None
    event_type: EventType = EventType.SOLO_WORK
    defense_aggression: DefenseAggression = DefenseAggression.DEFAULT
    description: Optional[str] = None
    enabled: bool = True
    time_policy_type: Optional[TimePolicyType] = None

    @field_validator("duration_max_mins")
    @classmethod
    def validate_duration_max_positive(cls, v: Optional[int]) -> Optional[int]:
        """Validate duration_max_mins is positive when provided."""
        if v is not None and v <= 0:
            raise ValueError("duration_max_mins must be greater than 0")
        return v

    @field_validator("ideal_time")
    @classmethod
    def validate_ideal_time(cls, v: str) -> str:
        """Validate ideal_time is in HH:MM or HH:MM:SS format."""
        if not re.match(r"^\d{2}:\d{2}(:\d{2})?$", v):
            raise ValueError("ideal_time must be in HH:MM or HH:MM:SS format (e.g., '09:00')")
        parts = v.split(":")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23):
            raise ValueError("hour must be between 00 and 23")
        if not (0 <= minute <= 59):
            raise ValueError("minute must be between 00 and 59")
        return v

    @model_validator(mode="after")
    def validate_habit_constraints(self) -> "HabitCreate":
        """Validate cross-field constraints."""
        # Duration constraints
        if self.duration_max_mins is not None:
            if self.duration_min_mins > self.duration_max_mins:
                raise ValueError("duration_min_mins cannot exceed duration_max_mins")

        # Frequency + ideal_days constraints
        if self.frequency == HabitFrequency.DAILY and self.ideal_days is not None:
            raise ValueError("ideal_days cannot be used with DAILY frequency")

        return self


class HabitUpdate(BaseModel):
    """Validation model for updating a habit."""

    title: Optional[str] = None
    ideal_time: Optional[str] = None
    duration_min_mins: Optional[int] = Field(default=None)
    duration_max_mins: Optional[int] = Field(default=None)
    enabled: Optional[bool] = None
    frequency: Optional[HabitFrequency] = None
    ideal_days: Optional[list[DayOfWeek]] = None
    event_type: Optional[EventType] = None
    defense_aggression: Optional[DefenseAggression] = None
    description: Optional[str] = None

    @field_validator("duration_min_mins", "duration_max_mins")
    @classmethod
    def validate_durations_positive(cls, v: Optional[int]) -> Optional[int]:
        """Validate duration fields are positive when provided."""
        if v is not None and v <= 0:
            raise ValueError("duration must be greater than 0")
        return v

    @field_validator("ideal_time")
    @classmethod
    def validate_ideal_time(cls, v: Optional[str]) -> Optional[str]:
        """Validate ideal_time is in HH:MM or HH:MM:SS format."""
        if v is None:
            return v
        if not re.match(r"^\d{2}:\d{2}(:\d{2})?$", v):
            raise ValueError("ideal_time must be in HH:MM or HH:MM:SS format (e.g., '09:00')")
        parts = v.split(":")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23):
            raise ValueError("hour must be between 00 and 23")
        if not (0 <= minute <= 59):
            raise ValueError("minute must be between 00 and 59")
        return v

    @model_validator(mode="after")
    def validate_update_constraints(self) -> "HabitUpdate":
        """Validate cross-field constraints for updates."""
        # Duration constraints (if both provided)
        if self.duration_min_mins is not None and self.duration_max_mins is not None:
            if self.duration_min_mins > self.duration_max_mins:
                raise ValueError("duration_min_mins cannot exceed duration_max_mins")

        # Frequency + ideal_days constraints
        if self.frequency == HabitFrequency.DAILY and self.ideal_days is not None:
            raise ValueError("ideal_days cannot be used with DAILY frequency")

        return self


# --- Event Validation Models ---


class EventRsvp(BaseModel):
    """Validation model for setting event RSVP status."""

    calendar_id: int
    event_id: str
    rsvp_status: RsvpStatus


class EventMove(BaseModel):
    """Validation model for moving/rescheduling an event.

    Note: v0.7.4+ uses the v1 API endpoint which doesn't require calendar_id.
    """

    event_id: str
    start_time: str
    end_time: str

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_datetime_format(cls, v: str) -> str:
        """Validate datetime is in ISO format."""
        # Accept ISO 8601 formats: 2026-01-02T14:00:00Z or 2026-01-02T14:00:00+00:00
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
        if not re.match(iso_pattern, v):
            raise ValueError("datetime must be in ISO format (e.g., '2026-01-02T14:00:00Z')")
        return v

    @model_validator(mode="after")
    def validate_time_order(self) -> "EventMove":
        """Validate that start_time is before end_time."""
        # Parse datetimes for comparison
        try:
            start = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
            if start >= end:
                raise ValueError("start_time must be before end_time")
        except ValueError as e:
            if "start_time must be before end_time" in str(e):
                raise
            # If parsing fails, the format validator already caught it
            pass
        return self


# --- Time Logging Validation Models ---


class TimeLog(BaseModel):
    """Validation model for logging time to a task."""

    minutes: int = Field(gt=0)


# --- Focus Settings Validation Models ---


class FocusSettingsUpdate(BaseModel):
    """Validation model for updating focus settings."""

    min_duration_mins: Optional[int] = Field(default=None)
    ideal_duration_mins: Optional[int] = Field(default=None)
    max_duration_mins: Optional[int] = Field(default=None)
    defense_aggression: Optional[DefenseAggression] = None
    enabled: Optional[bool] = None

    @field_validator("min_duration_mins", "ideal_duration_mins", "max_duration_mins")
    @classmethod
    def validate_durations_positive(cls, v: Optional[int]) -> Optional[int]:
        """Validate duration fields are positive when provided."""
        if v is not None and v <= 0:
            raise ValueError("duration must be greater than 0")
        return v

    @model_validator(mode="after")
    def validate_duration_order(self) -> "FocusSettingsUpdate":
        """Validate duration fields are in logical order when multiple provided."""
        # Check ordering: min <= ideal <= max
        if self.min_duration_mins is not None and self.ideal_duration_mins is not None:
            if self.min_duration_mins > self.ideal_duration_mins:
                raise ValueError("min_duration_mins cannot exceed ideal_duration_mins")
        if self.ideal_duration_mins is not None and self.max_duration_mins is not None:
            if self.ideal_duration_mins > self.max_duration_mins:
                raise ValueError("ideal_duration_mins cannot exceed max_duration_mins")
        if self.min_duration_mins is not None and self.max_duration_mins is not None:
            if self.min_duration_mins > self.max_duration_mins:
                raise ValueError("min_duration_mins cannot exceed max_duration_mins")

        return self


class FocusReschedule(BaseModel):
    """Validation model for reschedule_focus_block parameters."""

    calendar_id: int = Field(gt=0)
    event_id: str = Field(min_length=1)
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_datetime_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate datetime is in ISO format."""
        if v is None:
            return v
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
        if not re.match(iso_pattern, v):
            raise ValueError("datetime must be in ISO format (e.g., '2026-01-02T14:00:00Z')")
        return v


# --- ID Validation Models ---


class TaskId(BaseModel):
    """Validation for task ID parameters."""

    task_id: int = Field(gt=0)


class HabitId(BaseModel):
    """Validation for habit lineage ID parameters."""

    lineage_id: int = Field(gt=0)


class CalendarEventId(BaseModel):
    """Validation for calendar/event ID parameters."""

    calendar_id: int = Field(gt=0)
    event_id: str = Field(min_length=1)


class EventInstanceId(BaseModel):
    """Validation for event instance ID parameters (habit instances)."""

    event_id: str = Field(min_length=1)


# --- Date Range Validation Models ---


class DateRange(BaseModel):
    """Validation for date range parameters."""

    start: str
    end: str

    @field_validator("start", "end")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date is in YYYY-MM-DD format."""
        return cast(str, _validate_date_format(v))

    @model_validator(mode="after")
    def validate_date_order(self) -> "DateRange":
        """Validate that start date is before or equal to end date."""
        start_date = datetime.strptime(self.start, "%Y-%m-%d")
        end_date = datetime.strptime(self.end, "%Y-%m-%d")
        if start_date > end_date:
            raise ValueError("start date must be before or equal to end date")
        return self


class OptionalDateRange(BaseModel):
    """Validation for optional date range parameters."""

    start: Optional[str] = None
    end: Optional[str] = None

    @field_validator("start", "end")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date is in YYYY-MM-DD format if provided."""
        if v is None:
            return v
        return _validate_date_format(v)


# --- List Parameter Models ---


class ListLimit(BaseModel):
    """Validation for list limit parameters."""

    limit: int = Field(default=50, gt=0, le=1000)


class TaskListParams(BaseModel):
    """Validation for list_tasks parameters."""

    status: str = "NEW,SCHEDULED,IN_PROGRESS"
    limit: int = Field(default=50, gt=0, le=1000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status values are valid TaskStatus values."""
        valid = {"NEW", "SCHEDULED", "IN_PROGRESS", "COMPLETE", "ARCHIVED"}
        parts = [s.strip() for s in v.split(",")]
        invalid = set(parts) - valid
        if invalid:
            raise ValueError(f"invalid status values: {invalid}. Must be one of {valid}")
        return v


# --- Analytics Validation Models ---


class AnalyticsMetric(str, Enum):
    """Valid metric names for user analytics.

    Note: HOURS_DEFENDED and FOCUS_WORK_BALANCE were removed in v0.8.0
    because the Reclaim.ai V3 API returns 400 Bad Request for these metrics.
    """

    DURATION_BY_CATEGORY = "DURATION_BY_CATEGORY"
    DURATION_BY_DATE_BY_CATEGORY = "DURATION_BY_DATE_BY_CATEGORY"


class UserAnalyticsRequest(BaseModel):
    """Validation for get_user_analytics parameters."""

    start: str
    end: str
    metric_name: AnalyticsMetric

    @field_validator("start", "end")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date is in YYYY-MM-DD format."""
        return cast(str, _validate_date_format(v))


# --- Scheduling Validation Models ---


class SuggestedTimesRequest(BaseModel):
    """Validation for find_available_times parameters."""

    attendees: list[str] = Field(min_length=1, description="Email addresses of attendees")
    duration_minutes: int = Field(gt=0, le=480, description="Meeting duration in minutes")
    start_date: Optional[str] = Field(default=None, description="Start of search window (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End of search window (YYYY-MM-DD)")
    limit: Optional[int] = Field(default=None, gt=0, le=50, description="Max suggested times to return")

    @model_validator(mode="after")
    def validate_date_window(self) -> "SuggestedTimesRequest":
        """Validate that start_date and end_date are provided together."""
        if (self.start_date is None) != (self.end_date is None):
            raise ValueError("start_date and end_date must be provided together")
        if self.start_date:
            _validate_date_format(self.start_date)
        if self.end_date:
            _validate_date_format(self.end_date)
        return self
