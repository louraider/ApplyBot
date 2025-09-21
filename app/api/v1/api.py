#this will be handling all the api endpoints in my applicaiton
from fastapi import APIRouter
from app.api.v1.endpoints import health, jobs, users, projects, resume, cover_letters

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
api_router.include_router(cover_letters.router, prefix="/cover-letters", tags=["cover-letters"])