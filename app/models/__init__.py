"""
Database models package.
Import all models here to ensure they are registered with SQLAlchemy.
"""

from app.models.user import User
from app.models.project import Project
from app.models.job import Job
from app.models.application import Application

# Export all models
__all__ = ["User", "Project", "Job", "Application"]