"""Pydantic models for Task requests and responses."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Model for creating a new task."""
    title: str = Field(..., min_length=1, description="Task title cannot be empty")
    description: Optional[str] = Field(default="", description="Optional task description")
    page: str = Field(..., min_length=1, description="Page/project name cannot be empty")
    priority: Optional[str] = Field(default="Medium", description="Task priority (Low, Medium, High)")
    assigned_to: Optional[list[str]] = Field(default=[], description="List of user IDs to assign task to")


class TaskUpdate(BaseModel):
    """Model for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    page: Optional[str] = Field(default=None, min_length=1, description="Page/project name")
    priority: Optional[str] = Field(default=None, description="Task priority (Low, Medium, High)")
    assigned_to: Optional[list[str]] = Field(default=None, description="List of user IDs to assign task to")


class TaskResponse(BaseModel):
    """Model for task API responses."""
    id: str
    title: str
    description: str
    page: str
    status: str
    priority: str
    order: int
    assigned_to: list[str] = []
    assigned_to_usernames: list[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskReorder(BaseModel):
    """Model for reordering tasks."""
    task_ids: list[str]
