"""
Project service - simplified for existing database schema.
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.project import Project
from datetime import datetime, timezone
from loguru import logger


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_project(self, project_data: Dict[str, Any]) -> Project:
        """Create a new project using existing database fields only."""
        
        project = Project(
            user_id=project_data["user_id"],
            title=project_data["title"],
            description=project_data["description"],
            project_type=project_data.get("category"),  # Map category to project_type
            technologies=project_data.get("technologies", []),
            skills_demonstrated=project_data.get("skills_demonstrated", []),
            achievements=project_data.get("achievments", []),  # Note: typo in your JSON
            project_url=project_data.get("project_url") or project_data.get("url")
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def get_user_projects(
        self, 
        user_id: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Project]:
        """Get all projects for a user."""
        query = self.db.query(Project).filter(Project.user_id == user_id)
        
        if filters:
            if "project_type" in filters:
                query = query.filter(Project.project_type == filters["project_type"])
            if "technology" in filters:
                query = query.filter(Project.technologies.contains([filters["technology"]]))
        
        return query.offset(offset).limit(limit).all()
    
    def get_project_by_id(self, project_id: str, user_id: str) -> Optional[Project]:
        """Get a specific project by ID and user ID."""
        return self.db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
    
    def update_project(
        self, 
        project_id: str, 
        user_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Project]:
        """Update an existing project."""
        project = self.get_project_by_id(project_id, user_id)
        
        if not project:
            return None
        
        for key, value in update_data.items():
            if hasattr(project, key):  # Only update existing fields
                setattr(project, key, value)
        
        project.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete a project."""
        project = self.get_project_by_id(project_id, user_id)
        
        if not project:
            return False
        
        self.db.delete(project)
        self.db.commit()
        
        return True
