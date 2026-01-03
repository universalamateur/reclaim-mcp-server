"""Pydantic models for Reclaim.ai API responses."""

import re
from datetime import datetime
from enum import Enum
from typing import Optional

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


class RsvpStatus(str, Enum):
    """RSVP status values for calendar events."""

    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    TENTATIVE = "TENTATIVE"
    NEEDS_ACTION = "NEEDS_ACTION"


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
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    status: Optional[TaskStatus] = None
    due_date: Optional[str] = None

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


# --- Habit Validation Models ---


class HabitCreate(BaseModel):
    """Validation model for creating a habit."""

    title: str
    ideal_time: str
    duration_min_mins: int = Field(gt=0)
    duration_max_mins: Optional[int] = Field(default=None, gt=0)
    frequency: HabitFrequency = HabitFrequency.WEEKLY
    ideal_days: Optional[list[DayOfWeek]] = None
    event_type: EventType = EventType.SOLO_WORK
    defense_aggression: DefenseAggression = DefenseAggression.DEFAULT
    description: Optional[str] = None
    enabled: bool = True
    time_policy_type: Optional[TimePolicyType] = None

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
    duration_min_mins: Optional[int] = Field(default=None, gt=0)
    duration_max_mins: Optional[int] = Field(default=None, gt=0)
    enabled: Optional[bool] = None
    frequency: Optional[HabitFrequency] = None
    ideal_days: Optional[list[DayOfWeek]] = None
    event_type: Optional[EventType] = None
    defense_aggression: Optional[DefenseAggression] = None
    description: Optional[str] = None

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
    """Validation model for moving/rescheduling an event."""

    calendar_id: int
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
