#this will tell, how the projects are gettingstored in the Daatabase
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database.base import Base


class Project(Base):
    __tablename__ = "projects"
    
    # Primary key
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to user
    user_id=Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Project information
    title=Column(String(255), nullable=False)
    description=Column(Text, nullable=False)
    duration=Column(String(100), nullable=True)  # e.g., "3 months", "2020-2021"
    project_type=Column(String(100), nullable=True)  # e.g., "Full-Stack", "AI", "Mobile"
    
    # Technology tags and achievements (PostgreSQL arrays)
    technologies=Column(ARRAY(String), nullable=False, default=[])
    achievements=Column(ARRAY(String), nullable=False, default=[])
    
    # User-defined priority for project selection (1-10)
    priority=Column(Integer, default=5, nullable=False)
    
    # Optional project link
    project_url=Column(String(255), nullable=True)
    
    # Timestamps
    created_at=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user=relationship("User", back_populates="projects")
    
    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title}, user_id={self.user_id})>"