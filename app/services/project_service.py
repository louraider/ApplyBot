"""
Project service for database operations.
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database.models import Project
from datetime import datetime, timezone
from loguru import logger

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_project(self, project_data: Dict[str, Any]) -> Project:
        """Create a new project."""
        project = Project(
            id=project_data["id"],
            user_id=project_data["user_id"],
            title=project_data["title"],
            description=project_data["description"],
            technologies=project_data.get("technologies", []),
            category=project_data["category"],
            difficulty_level=project_data.get("difficulty_level", "Intermediate"),
            duration=project_data.get("duration"),
            team_size=project_data.get("team_size", 1),
            url=project_data.get("url"),
            status=project_data.get("status", "Completed"),
            highlights=project_data.get("highlights", []),
            metrics=project_data.get("metrics", {}),
            skills_demonstrated=project_data.get("skills_demonstrated", []),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
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
        """Get all projects for a user with optional filtering."""
        query = self.db.query(Project).filter(Project.user_id == user_id)
        
        if filters:
            if "category" in filters:
                query = query.filter(Project.category == filters["category"])
            if "status" in filters:
                query = query.filter(Project.status == filters["status"])
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
