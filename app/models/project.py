"""
Project model - simplified to match existing database schema.
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database.base import Base

class Project(Base):
    __tablename__ = "projects"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to user  
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Project information (existing fields only)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    project_type = Column(String(100), nullable=True)
    category=Column(String(100), nullable=False)
    # Technology tags and achievements (existing fields)
    technologies = Column(ARRAY(String), nullable=False, default=[])
    achievements = Column(ARRAY(String), nullable=False, default=[])
    skills_demonstrated = Column(ARRAY(String), nullable=False, default=[])
    
    # Optional project link (existing field)
    project_url = Column(String(255), nullable=True)
    
    # Timestamps (existing fields)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    
    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title}, user_id={self.user_id})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "project_type": self.project_type,
            "technologies": self.technologies or [],
            "skills_demonstrated": self.skills_demonstrated or [],
            "project_url": self.project_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
