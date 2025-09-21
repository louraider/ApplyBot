#will define the application model

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database.base import Base


class Application(Base):
    __tablename__ = "applications"
    
    # Primary key
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    user_id=Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    job_id=Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Batch processing tracking
    batch_id=Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Generated content paths
    resume_path=Column(String(255), nullable=True)
    cover_letter=Column(Text, nullable=True)
    
    # Email content
    email_subject=Column(String(255), nullable=True)
    email_body=Column(Text, nullable=True)
    
    # Application status tracking
    status=Column(String(50), default="pending", nullable=False, index=True)
    # Status values: pending, sent, response_received, no_response, follow_up_sent
    
    # Timestamps
    created_at=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sent_at=Column(DateTime(timezone=True), nullable=True)
    response_received_at=Column(DateTime(timezone=True), nullable=True)
    follow_up_scheduled_at=Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user=relationship("User", back_populates="applications")
    job=relationship("Job", back_populates="applications")
    
    def __repr__(self):
        return f"<Application(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, status={self.status})>"