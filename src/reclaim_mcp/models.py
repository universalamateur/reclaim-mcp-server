"""Pydantic models for Reclaim.ai API responses."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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
    """Request model for creating a task."""

    title: str
    time_chunks_required: int = Field(alias="timeChunksRequired")
    min_chunk_size: int = Field(default=15, alias="minChunkSize")
    max_chunk_size: Optional[int] = Field(default=None, alias="maxChunkSize")
    due: Optional[str] = None
    snooze_until: Optional[str] = Field(default=None, alias="snoozeUntil")

    model_config = {"populate_by_name": True}


class TaskUpdate(BaseModel):
    """Request model for updating a task."""

    title: Optional[str] = None
    time_chunks_required: Optional[int] = Field(default=None, alias="timeChunksRequired")
    status: Optional[TaskStatus] = None
    due: Optional[str] = None

    model_config = {"populate_by_name": True}
