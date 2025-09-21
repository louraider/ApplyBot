"""
Resume generation endpoints with job-specific file organization.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from loguru import logger
import os
from pathlib import Path
import uuid
from datetime import datetime, timezone  # Add timezone import
from app.database.base import get_db
from app.services.resume_generator import resume_generator, ResumeGenerationError

router = APIRouter()

class EducationItem(BaseModel):
    """Education item model."""
    degree: str
    institution: str
    year: str
    coursework: Optional[str] = None
    gpa: Optional[str] = None

class SkillCategory(BaseModel):
    """Skill category model."""
    category: str
    items: List[str]

class ExperienceItem(BaseModel):
    """Experience item model."""
    role: str
    company: str
    duration: str
    location: str
    achievements: List[str]

class ProjectItem(BaseModel):
    """Project item model."""
    title: str
    description: str
    technologies: Optional[List[str]] = None
    url: Optional[str] = None

class ResumeGenerationRequest(BaseModel):
    """Request model for resume generation."""
    
    # Personal Information
    name: str
    phone: str
    location: str
    email: str
    linkedin_url: Optional[str] = None
    linkedin_display: Optional[str] = None
    website_url: Optional[str] = None
    website_display: Optional[str] = None
    
    # Professional Information
    experience_years: Optional[str] = "2+"
    primary_skills: Optional[List[str]] = ["Software Development"]
    
    # Resume Sections
    education: Optional[List[EducationItem]] = []
    skills: Optional[List[SkillCategory]] = []
    experience: Optional[List[ExperienceItem]] = []
    projects: Optional[List[ProjectItem]] = []
    extra_curricular: Optional[List[str]] = []
    leadership: Optional[List[str]] = []
    
    # Customization
    job_id: Optional[str] = None  # For job-specific customization
    selected_project_ids: Optional[List[str]] = None  # Specific projects to include

class ResumeResponse(BaseModel):
    """Enhanced response model for resume generation."""
    success: bool
    resume_id: str
    job_id: Optional[str] = None
    download_url: str
    template_url: Optional[str] = None
    generation_method: str
    file_paths: Optional[Dict[str, Optional[str]]] = None  # FIXED: Allow None values
    created_at: str
    user_name: str
    job_title: Optional[str] = None
    message: str


class JobFilesResponse(BaseModel):
    """Response model for job-specific files."""
    job_id: str
    exists: bool
    templates: Dict[str, Any]
    pdfs: Dict[str, Any]
    files_count: int

@router.post("/generate", response_model=ResumeResponse)
async def generate_resume(
    request: ResumeGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate a customized resume PDF with job-specific file organization."""
    try:
        logger.info(f"Generating resume for {request.name}")
        
        # Convert request to dict for template
        user_data = request.dict()
        
        # Get job context if job_id provided - WITH BETTER ERROR HANDLING
        job_context = None
        if request.job_id:
            try:
                job_context = await _get_job_context(request.job_id, db)
                logger.info(f"Job context retrieved for {request.job_id}: {job_context}")
            except Exception as job_error:
                # Log the job context error but continue without it
                logger.warning(f"Could not get job context for {request.job_id}: {job_error}")
                # Create a default job context to avoid breaking resume generation
                job_context = {
                    "title": "Software Engineer",
                    "company": "Tech Company", 
                    "description": f"Position with job ID: {request.job_id}",
                    "requirements": [],
                    "location": "Remote"
                }
        
        # Get selected projects
        selected_projects = None
        if request.selected_project_ids and request.projects:
            selected_projects = _filter_projects_by_ids(
                request.projects, request.selected_project_ids
            )
            logger.info(f"Selected {len(selected_projects)} specific projects")
        elif request.projects:
            # Use all projects if none specifically selected
            selected_projects = [proj.dict() for proj in request.projects]
            logger.info(f"Using all {len(selected_projects)} projects")
        else:
            logger.info("No projects provided")
        
        # FIXED: Check if resume_generator supports job_id parameter
        try:
            # Try the new method signature first
            result = resume_generator.generate_resume(
                user_data=user_data,
                selected_projects=selected_projects,
                job_context=job_context,
                job_id=request.job_id  # NEW: Pass job_id for organized storage
            )
            logger.info(f"Resume generated with job_id support: {result['resume_id']}")
        except TypeError as method_error:
            # If the method doesn't support job_id, fall back to old signature
            if "unexpected keyword argument 'job_id'" in str(method_error):
                logger.warning("resume_generator doesn't support job_id parameter, using legacy method")
                result = resume_generator.generate_resume(
                    user_data=user_data,
                    selected_projects=selected_projects,
                    job_context=job_context
                )
                # Manually add job_id to result if it was provided
                if request.job_id:
                    result["job_id"] = request.job_id
                    result["resume_id"] = request.job_id  # Use job_id as resume_id
                logger.info(f"Resume generated with legacy method: {result['resume_id']}")
            else:
                # Re-raise if it's a different TypeError
                raise method_error
        
        # Prepare response URLs
        base_url = "/api/v1/resume"
        download_url = f"{base_url}/download/{result['resume_id']}"
        template_url = None
        
        # Check if job-specific files were created
        if request.job_id and "template_path" in result:
            template_url = f"{base_url}/download/{result['resume_id']}/template"
        
        # BUILD RESPONSE WITH SAFE DEFAULTS
        response = ResumeResponse(
            success=True,
            resume_id=result.get("resume_id", str(uuid.uuid4())),
            job_id=request.job_id,
            download_url=download_url,
            template_url=template_url,
            generation_method=result.get("generation_method", "unknown"),
            file_paths={
                "pdf": result.get("pdf_path", result.get("file_path")),
                "template": result.get("template_path")
            } if request.job_id else {"pdf": result.get("file_path")},
            created_at=result.get("created_at", datetime.now(timezone.utc).isoformat()),
            user_name=result.get("user_name", request.name),
            job_title=result.get("job_title", job_context.get("title", "General") if job_context else "General"),
            message=f"Resume generated successfully using {result.get('generation_method', 'unknown')}" + 
                   (f" for job {request.job_id}" if request.job_id else "")
        )
        
        logger.info(f"Resume generation completed successfully: {response.resume_id}")
        return response
        
    except ResumeGenerationError as e:
        logger.error(f"Resume generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error generating resume: {e}")
        # More detailed error for debugging
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")


@router.get("/download/{resume_id}")
async def download_resume(resume_id: str):
    """Download a generated resume PDF (supports both legacy and job-specific)."""
    try:
        # Check if this is a job-specific resume
        if resume_id.startswith("job_") or len(resume_id.split("-")) == 5:  # UUID format
            job_files = resume_generator.get_job_files(resume_id)
            
            if not job_files["exists"]:
                raise HTTPException(status_code=404, detail="Resume not found")
            
            # Get PDF path from job files
            if "files" in job_files["pdfs"] and "resume" in job_files["pdfs"]["files"]:
                file_path = Path(job_files["pdfs"]["files"]["resume"]["path"])
                filename = f"resume_{resume_id}.pdf"
            else:
                raise HTTPException(status_code=404, detail="Resume PDF not found")
        else:
            # Legacy resume handling
            file_path = resume_generator.get_resume_path(resume_id)
            filename = f"resume_{resume_id}.pdf"
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to download resume")

@router.get("/download/{resume_id}")
async def download_resume(resume_id: str):
    """Download a generated resume PDF with proper filename."""
    try:
        # Check if this is a job-specific resume
        if resume_id.startswith("job_") or len(resume_id.split("-")) == 5:  # UUID format
            job_files = resume_generator.get_job_files(resume_id)
            
            if not job_files["exists"]:
                raise HTTPException(status_code=404, detail="Resume not found")
            
            # Get PDF path from job files
            if "files" in job_files["pdfs"] and "resume" in job_files["pdfs"]["files"]:
                file_path = Path(job_files["pdfs"]["files"]["resume"]["path"])
                # Use the actual filename from the path
                filename = file_path.name
            else:
                raise HTTPException(status_code=404, detail="Resume PDF not found")
        else:
            # Legacy resume handling - try both naming conventions
            user_name_file = None
            
            # First, try to find with new naming convention
            for pdf_file in resume_generator.output_dir.glob(f"*_{resume_id}.pdf"):
                if pdf_file.exists():
                    file_path = pdf_file
                    filename = pdf_file.name
                    break
            else:
                # Fallback to old naming convention
                file_path = resume_generator.get_resume_path(resume_id)
                filename = f"resume_{resume_id}.pdf"
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,  # Use the actual filename
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to download resume")


@router.get("/job/{job_id}/files", response_model=JobFilesResponse)
async def get_job_files(job_id: str):
    """Get all files associated with a specific job ID."""
    try:
        logger.info(f"Getting files for job {job_id}")
        
        job_files = resume_generator.get_job_files(job_id)
        
        if not job_files["exists"]:
            raise HTTPException(status_code=404, detail=f"No files found for job {job_id}")
        
        # Count total files
        files_count = 0
        if job_files["templates"]:
            files_count += 1
        if "files" in job_files["pdfs"]:
            files_count += len(job_files["pdfs"]["files"])
        
        return JobFilesResponse(
            job_id=job_id,
            exists=job_files["exists"],
            templates=job_files["templates"],
            pdfs=job_files["pdfs"],
            files_count=files_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting files for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job files")

@router.delete("/{resume_id}")
async def delete_resume(resume_id: str):
    """Delete resume and associated files."""
    try:
        logger.info(f"Deleting resume {resume_id}")
        
        # Check if this is a job-specific resume
        if resume_id.startswith("job_") or len(resume_id.split("-")) == 5:  # UUID format
            job_files = resume_generator.get_job_files(resume_id)
            
            if not job_files["exists"]:
                raise HTTPException(status_code=404, detail="Resume not found")
            
            # Delete job-specific directories
            import shutil
            
            # Delete template directory
            template_dir = resume_generator.storage_service.generated_templates_dir / f"job_{resume_id}"
            if template_dir.exists():
                shutil.rmtree(template_dir)
                logger.info(f"Deleted template directory: {template_dir}")
            
            # Delete resume directory
            resume_dir = resume_generator.storage_service.resumes_dir / f"job_{resume_id}"
            if resume_dir.exists():
                shutil.rmtree(resume_dir)
                logger.info(f"Deleted resume directory: {resume_dir}")
            
            return {
                "success": True,
                "resume_id": resume_id,
                "message": f"Resume {resume_id} and all associated files deleted successfully"
            }
        else:
            # Legacy resume deletion
            file_path = resume_generator.get_resume_path(resume_id)
            
            if file_path and file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted legacy resume: {file_path}")
                return {
                    "success": True,
                    "resume_id": resume_id,
                    "message": f"Resume {resume_id} deleted successfully"
                }
            else:
                raise HTTPException(status_code=404, detail="Resume not found")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resume {resume_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete resume")

@router.get("/list")
async def list_resumes(
    user_id: Optional[str] = None,
    job_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all resumes with optional filtering and proper filenames."""
    try:
        logger.info(f"Listing resumes (user_id: {user_id}, job_id: {job_id})")
        
        resumes = []
        
        # Scan job-specific resumes (if storage_service exists)
        if hasattr(resume_generator, 'storage_service'):
            # ... existing job-specific scanning code ...
            pass
        
        # Scan legacy resumes with both naming conventions
        legacy_dir = Path("app/generated/resumes")
        if legacy_dir.exists():
            # Check for new naming convention first
            for file_path in legacy_dir.glob("*_*.pdf"):
                if file_path.name.startswith("resume_"):
                    continue  # Skip old format, will be handled below
                    
                # Extract name and job_id from filename
                stem = file_path.stem
                parts = stem.split("_")
                if len(parts) >= 2:
                    user_name = "_".join(parts[:-1])
                    job_id_from_name = parts[-1]
                    
                    stat = file_path.stat()
                    resumes.append({
                        "resume_id": job_id_from_name,
                        "job_id": job_id_from_name,
                        "user_name": user_name.replace("_", " ").title(),
                        "type": "named_format",
                        "file_path": str(file_path),
                        "filename": file_path.name,
                        "file_size": stat.st_size,
                        "created_at": stat.st_ctime,
                        "files_count": 1
                    })
            
            # Check for old naming convention
            for file_path in legacy_dir.glob("resume_*.pdf"):
                resume_id = file_path.stem.replace("resume_", "")
                if not any(r["resume_id"] == resume_id for r in resumes):  # Avoid duplicates
                    stat = file_path.stat()
                    resumes.append({
                        "resume_id": resume_id,
                        "job_id": None,
                        "user_name": "Unknown",
                        "type": "legacy",
                        "file_path": str(file_path),
                        "filename": file_path.name,
                        "file_size": stat.st_size,
                        "created_at": stat.st_ctime,
                        "files_count": 1
                    })
        
        # Apply job_id filter if provided
        if job_id:
            resumes = [r for r in resumes if r.get("job_id") == job_id]
        
        # Sort by creation time (newest first)
        resumes.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        
        # Apply pagination
        total = len(resumes)
        paginated_resumes = resumes[offset:offset + limit]
        
        return {
            "success": True,
            "resumes": paginated_resumes,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        logger.error(f"Error listing resumes: {e}")
        raise HTTPException(status_code=500, detail="Failed to list resumes")


@router.get("/template")
async def get_resume_template():
    """Get the resume template structure for frontend forms."""
    return {
        "success": True,
        "template": {
            "personal_info": {
                "name": "string (required)",
                "phone": "string (required)",
                "location": "string (required)",
                "email": "string (required)",
                "linkedin_url": "string (optional)",
                "linkedin_display": "string (optional)",
                "website_url": "string (optional)",
                "website_display": "string (optional)"
            },
            "professional_info": {
                "experience_years": "string (default: '2+')",
                "primary_skills": "array of strings"
            },
            "sections": {
                "education": [
                    {
                        "degree": "string",
                        "institution": "string",
                        "year": "string",
                        "coursework": "string (optional)",
                        "gpa": "string (optional)"
                    }
                ],
                "skills": [
                    {
                        "category": "string",
                        "items": ["array", "of", "strings"]
                    }
                ],
                "experience": [
                    {
                        "role": "string",
                        "company": "string",
                        "duration": "string",
                        "location": "string",
                        "achievements": ["array", "of", "strings"]
                    }
                ],
                "projects": [
                    {
                        "title": "string",
                        "description": "string",
                        "technologies": ["array", "of", "strings"],
                        "url": "string (optional)"
                    }
                ],
                "extra_curricular": ["array", "of", "strings"],
                "leadership": ["array", "of", "strings"]
            },
            "customization": {
                "job_id": "string (optional) - for job-specific customization",
                "selected_project_ids": ["array", "of", "project", "indices"]
            }
        }
    }

@router.get("/status")
async def get_resume_generator_status():
    """Get the status of resume generation capabilities."""
    status_info = {
        "latex_available": resume_generator.latex_available,
        "output_directory": str(resume_generator.output_dir),
        "template_directory": str(resume_generator.template_dir)
    }
    
    # Add job-specific directory info if available
    if hasattr(resume_generator, 'storage_service'):
        status_info.update({
            "job_templates_directory": str(resume_generator.storage_service.generated_templates_dir),
            "job_resumes_directory": str(resume_generator.storage_service.resumes_dir),
            "organized_storage": True
        })
    else:
        status_info["organized_storage"] = False
    
    # Try to get fallback availability
    try:
        status_info["reportlab_available"] = hasattr(resume_generator, 'REPORTLAB_AVAILABLE') and resume_generator.REPORTLAB_AVAILABLE
        status_info["weasyprint_available"] = hasattr(resume_generator, 'WEASYPRINT_AVAILABLE') and resume_generator.WEASYPRINT_AVAILABLE
    except:
        status_info["reportlab_available"] = False
        status_info["weasyprint_available"] = False
    
    return {
        "success": True,
        "status": status_info
    }

# Helper functions
async def _get_job_context(job_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Get job context for resume customization."""
    try:
        from app.services.job_service import JobService
        job_service = JobService(db)
        job = job_service.get_job_by_id(job_id)
        
        if job:
            return {
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "requirements": job.requirements or [],
                "location": job.location
            }
        return None
    except Exception as e:
        logger.warning(f"Could not get job context for {job_id}: {e}")
        return None

def _filter_projects_by_ids(
    all_projects: List[ProjectItem],
    selected_ids: List[str]
) -> List[Dict[str, Any]]:
    """Filter projects by selected IDs."""
    # For now, assume project IDs are indices
    # In a real implementation, you'd have actual project IDs
    selected_projects = []
    
    for project_id in selected_ids:
        try:
            index = int(project_id)
            if 0 <= index < len(all_projects):
                selected_projects.append(all_projects[index].dict())
        except (ValueError, IndexError):
            logger.warning(f"Invalid project ID: {project_id}")
    
    return selected_projects
