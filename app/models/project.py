"""
Project model for storing user projects with enhanced matching capabilities.
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, JSON
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
    
    # Basic project information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    duration = Column(String(100), nullable=True)  # e.g., "3 months", "2020-2021"
    
    # ENHANCED: More detailed categorization
    category = Column(String(100), nullable=False, default="Other")  # ADDED for matching
    project_type = Column(String(100), nullable=True)  # Keep your existing field
    difficulty_level = Column(String(50), default="Intermediate")  # ADDED: Beginner, Intermediate, Advanced
    team_size = Column(Integer, default=1)  # ADDED: For collaboration indication
    status = Column(String(50), default="Completed")  # ADDED: Completed, In Progress, Paused
    
    # Technology and skills (enhanced for matching)
    technologies = Column(ARRAY(String), nullable=False, default=[])
    skills_demonstrated = Column(ARRAY(String), nullable=False, default=[])  # ADDED for matching
    achievements = Column(ARRAY(String), nullable=False, default=[])  # Your existing field
    highlights = Column(ARRAY(String), nullable=False, default=[])  # ADDED: Key accomplishments
    
    # ENHANCED: Performance metrics and metadata
    metrics = Column(JSON, nullable=True, default={})  # ADDED: Store performance data, user counts, etc.
    
    # User-defined priority (keep your existing field)
    priority = Column(Integer, default=5, nullable=False)
    
    # Project links
    project_url = Column(String(255), nullable=True)  # Your existing field
    github_url = Column(String(255), nullable=True)  # ADDED: Separate GitHub link
    demo_url = Column(String(255), nullable=True)  # ADDED: Live demo link
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    
    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title}, user_id={self.user_id})>"
    
    # ADDED: Helper methods for the matching system
    @property
    def url(self) -> str:
        """Return the primary URL (for backward compatibility with matching system)."""
        return self.project_url or self.github_url or self.demo_url
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "category": self.category,
            "project_type": self.project_type,
            "difficulty_level": self.difficulty_level,
            "team_size": self.team_size,
            "status": self.status,
            "technologies": self.technologies or [],
            "skills_demonstrated": self.skills_demonstrated or [],
            "achievements": self.achievements or [],
            "highlights": self.highlights or [],
            "metrics": self.metrics or {},
            "priority": self.priority,
            "project_url": self.project_url,
            "github_url": self.github_url,
            "demo_url": self.demo_url,
            "url": self.url,  # Primary URL
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
