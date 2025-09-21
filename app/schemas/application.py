"""
Pydantic schemas for Application model validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class ApplicationBase(BaseModel):
    """Base application schema with common fields."""
    job_id: uuid.UUID
    batch_id: Optional[uuid.UUID] = None
    resume_path: Optional[str] = None
    cover_letter: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    status: str = "pending"


class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application."""
    pass


class ApplicationUpdate(BaseModel):
    """Schema for updating application information."""
    status: Optional[str] = None
    resume_path: Optional[str] = None
    cover_letter: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    sent_at: Optional[datetime] = None
    response_received_at: Optional[datetime] = None
    follow_up_scheduled_at: Optional[datetime] = None


class ApplicationResponse(ApplicationBase):
    """Schema for application response data."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    sent_at: Optional[datetime] = None
    response_received_at: Optional[datetime] = None
    follow_up_scheduled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApplicationWithDetails(ApplicationResponse):
    """Application response with job and user details."""
    job: "JobResponse"
    user: "UserResponse"