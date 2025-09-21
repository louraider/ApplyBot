"""
Pydantic schemas for Project model validation.
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import uuid


class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    title: str
    description: str
    duration: Optional[str] = None
    project_type: Optional[str] = None
    technologies: List[str] = []
    achievements: List[str] = []
    priority: int = 5
    project_url: Optional[str] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Priority must be between 1 and 10')
        return v
    
    @validator('technologies', 'achievements')
    def validate_arrays_not_empty(cls, v):
        if not v:
            return []
        return v


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating project information."""
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    project_type: Optional[str] = None
    technologies: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    priority: Optional[int] = None
    project_url: Optional[str] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None and not 1 <= v <= 10:
            raise ValueError('Priority must be between 1 and 10')
        return v


class ProjectResponse(ProjectBase):
    """Schema for project response data."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True