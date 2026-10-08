"""Pydantic models for Page requests and responses."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PageCreate(BaseModel):
    """Model for creating a new page."""
    name: str = Field(..., min_length=1, description="Page name cannot be empty")
    shared_with: Optional[list[str]] = Field(default=[], description="List of user IDs to share with")


class PageUpdate(BaseModel):
    """Model for updating a page."""
    name: Optional[str] = Field(default=None, min_length=1, description="Page name")
    shared_with: Optional[list[str]] = Field(default=None, description="List of user IDs to share with")


class PageResponse(BaseModel):
    """Model for page API responses."""
    id: str
    name: str
    created_by: str
    created_by_username: str
    shared_with: list[str]
    shared_with_usernames: list[str]
    created_at: datetime

    class Config:
        from_attributes = True
