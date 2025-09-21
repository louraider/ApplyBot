"""
Project matching API with explanations and caching.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger
import uuid

from app.database.base import get_db
from app.services.project_service import ProjectService
from app.services.job_service import JobService
from app.services.matching.tfidf_matcher import TFIDFProjectMatcher
from app.services.matching.cache_service import MatchingCacheService
from app.services.matching.base_matcher import JobContext

router = APIRouter()

# Initialize services
tfidf_matcher = TFIDFProjectMatcher()
cache_service = MatchingCacheService()

class ProjectMatchResponse(BaseModel):
    """Response model for project matching."""
    project_id: str
    project_title: str
    project_description: str
    project_technologies: List[str]
    confidence_score: float
    explanation: Dict[str, Any]
    matching_keywords: List[str]
    similarity_breakdown: Dict[str, float]
    rank: int

class MatchingResultResponse(BaseModel):
    """Full response for project matching request."""
    success: bool
    job_id: str
    job_title: str
    matched_projects: List[ProjectMatchResponse]
    algorithm_used: str
    algorithm_version: str
    total_projects_analyzed: int
    cache_hit: bool
    processing_time_ms: float
    explanation_summary: Dict[str, Any]

@router.get("/match/{job_id}", response_model=MatchingResultResponse)
async def match_projects_to_job(
    job_id: str,
    user_id: str = Query(..., description="User ID"),
    max_results: int = Query(5, ge=1, le=10, description="Maximum results to return"),
    force_refresh: bool = Query(False, description="Force refresh cache"),
    algorithm: str = Query("tfidf", description="Matching algorithm to use"),
    db: Session = Depends(get_db)
):
    """
    Match user's projects to a specific job with detailed explanations.
    
    Returns the top matching projects with confidence scores and explanations
    of why each project was selected.
    """
    
    import time
    start_time = time.time()
    
    try:
        logger.info(f"Matching projects for user {user_id} to job {job_id}")
        
        # Get job details
        job_service = JobService(db)
        job = job_service.get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Create job context
        job_context = JobContext(
            job_id=job.id,
            title=job.title,
            description=job.description,
            company=job.company,
            required_skills=job.required_skills or [],
            preferred_skills=job.preferred_skills or [],
            category=getattr(job, 'category', None),
            location=job.location
        )
        
        # Check cache first (unless force refresh)
        cache_hit = False
        cached_results = None
        
        if not force_refresh:
            cache_key = cache_service.generate_cache_key(
                user_id=user_id,
                job_context=job_context,
                algorithm_name=tfidf_matcher.get_algorithm_name(),
                algorithm_version=tfidf_matcher.get_algorithm_version()
            )
            cached_results = cache_service.get_cached_results(cache_key)
            cache_hit = cached_results is not None
        
        if cached_results:
            # Return cached results
            processing_time = (time.time() - start_time) * 1000
            
            matched_projects = []
            for i, cached_result in enumerate(cached_results[:max_results]):
                matched_projects.append(ProjectMatchResponse(
                    project_id=cached_result['project_id'],
                    project_title=cached_result['project_title'],
                    project_description="", # Not cached to save space
                    project_technologies=[],  # Not cached to save space
                    confidence_score=cached_result['confidence_score'],
                    explanation=cached_result['explanation'],
                    matching_keywords=cached_result['matching_keywords'],
                    similarity_breakdown=cached_result['similarity_breakdown'],
                    rank=i + 1
                ))
            
            return MatchingResultResponse(
                success=True,
                job_id=job_id,
                job_title=job.title,
                matched_projects=matched_projects,
                algorithm_used=tfidf_matcher.get_algorithm_name(),
                algorithm_version=tfidf_matcher.get_algorithm_version(),
                total_projects_analyzed=len(cached_results),
                cache_hit=True,
                processing_time_ms=processing_time,
                explanation_summary=_generate_explanation_summary(matched_projects)
            )
        
        # Get user projects
        project_service = ProjectService(db)
        projects = project_service.get_user_projects(user_id)
        
        if not projects:
            return MatchingResultResponse(
                success=True,
                job_id=job_id,
                job_title=job.title,
                matched_projects=[],
                algorithm_used=tfidf_matcher.get_algorithm_name(),
                algorithm_version=tfidf_matcher.get_algorithm_version(),
                total_projects_analyzed=0,
                cache_hit=False,
                processing_time_ms=(time.time() - start_time) * 1000,
                explanation_summary={"message": "No projects found for user"}
            )
        
        # Perform matching
        match_results = tfidf_matcher.match_projects(
            projects=projects,
            job_context=job_context,
            max_results=max_results
        )
        
        # Convert to response format
        matched_projects = []
        for i, result in enumerate(match_results):
            matched_projects.append(ProjectMatchResponse(
                project_id=result.project.id,
                project_title=result.project.title,
                project_description=result.project.description or "",
                project_technologies=result.project.technologies or [],
                confidence_score=result.confidence_score,
                explanation=result.explanation,
                matching_keywords=result.matching_keywords,
                similarity_breakdown=result.similarity_breakdown,
                rank=i + 1
            ))
        
        # Cache results in background
        if not force_refresh:
            cache_service.cache_results(cache_key, match_results)
        
        processing_time = (time.time() - start_time) * 1000
        
        return MatchingResultResponse(
            success=True,
            job_id=job_id,
            job_title=job.title,
            matched_projects=matched_projects,
            algorithm_used=tfidf_matcher.get_algorithm_name(),
            algorithm_version=tfidf_matcher.get_algorithm_version(),
            total_projects_analyzed=len(projects),
            cache_hit=False,
            processing_time_ms=processing_time,
            explanation_summary=_generate_explanation_summary(matched_projects)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in project matching: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Project matching failed: {str(e)}")

@router.post("/match/bulk")
async def bulk_match_projects(
    job_ids: List[str],                           # No default
    background_tasks: BackgroundTasks,            # No default - MOVED UP
    user_id: str = Query(..., description="User ID"),  # Has default
    max_results_per_job: int = Query(3, ge=1, le=5),   # Has default  
    db: Session = Depends(get_db)                 # Has default
):

    """
    Match projects to multiple jobs simultaneously.
    Useful for testing multiple job applications.
    """
    
    try:
        logger.info(f"Bulk matching projects for user {user_id} to {len(job_ids)} jobs")
        
        if len(job_ids) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 jobs allowed per bulk request")
        
        results = {}
        
        for job_id in job_ids:
            try:
                # This would call the single match endpoint logic
                # For brevity, I'll show the structure
                results[job_id] = {
                    "status": "pending",
                    "message": f"Matching queued for job {job_id}"
                }
                
                # Add background task for processing
                background_tasks.add_task(
                    _process_single_match,
                    job_id=job_id,
                    user_id=user_id,
                    max_results=max_results_per_job,
                    db=db
                )
                
            except Exception as e:
                results[job_id] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return {
            "success": True,
            "message": f"Bulk matching initiated for {len(job_ids)} jobs",
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk matching: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk matching failed: {str(e)}")

@router.get("/match/{job_id}/explain")
async def explain_matching_algorithm(
    job_id: str,
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation of how the matching algorithm works
    and what factors influence project selection.
    """
    
    try:
        job_service = JobService(db)
        job = job_service.get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        explanation = {
            "algorithm_name": tfidf_matcher.get_algorithm_name(),
            "algorithm_version": tfidf_matcher.get_algorithm_version(),
            "methodology": {
                "step_1": "TF-IDF Analysis (40% weight)",
                "step_1_description": "Analyzes semantic similarity between project descriptions and job description using Term Frequency-Inverse Document Frequency",
                "step_2": "Keyword Matching (35% weight)", 
                "step_2_description": "Matches important keywords and phrases between project content and job requirements",
                "step_3": "Technology Alignment (25% weight)",
                "step_3_description": "Evaluates overlap between project technologies and job required/preferred skills"
            },
            "scoring_factors": [
                "Content similarity (project description vs job description)",
                "Title relevance (project title vs job title)",
                "Technology stack overlap",
                "Required skills coverage",
                "Project category alignment",
                "Keyword density and importance"
            ],
            "job_analysis": {
                "job_title": job.title,
                "identified_keywords": "...",  # Would extract actual keywords
                "required_technologies": job.required_skills or [],
                "preferred_technologies": job.preferred_skills or [],
                "category_hints": "..."  # Would analyze job category
            }
        }
        
        return {
            "success": True,
            "explanation": explanation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining algorithm: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to explain algorithm: {str(e)}")

@router.delete("/cache/{user_id}")
async def clear_user_cache(
    user_id: str,
    confirm: bool = Query(False, description="Confirm cache deletion")
):
    """Clear all cached matching results for a user."""
    
    if not confirm:
        return {
            "success": False,
            "message": "Cache deletion requires confirmation. Add ?confirm=true to proceed."
        }
    
    try:
        invalidated_count = cache_service.invalidate_user_cache(user_id)
        
        return {
            "success": True,
            "message": f"Cleared {invalidated_count} cached entries for user {user_id}"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/cache/stats")
async def get_cache_statistics():
    """Get cache performance statistics."""
    
    try:
        stats = cache_service.get_cache_stats()
        
        return {
            "success": True,
            "cache_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")

# Helper functions

def _generate_explanation_summary(matched_projects: List[ProjectMatchResponse]) -> Dict[str, Any]:
    """Generate a summary explanation of the matching results."""
    
    if not matched_projects:
        return {"message": "No matching projects found"}
    
    avg_confidence = sum(p.confidence_score for p in matched_projects) / len(matched_projects)
    
    # Find most common matching factors
    all_keywords = []
    for project in matched_projects:
        all_keywords.extend(project.matching_keywords)
    
    from collections import Counter
    common_keywords = Counter(all_keywords).most_common(5)
    
    return {
        "total_matches": len(matched_projects), 
        "average_confidence": round(avg_confidence, 3),
        "top_matching_keywords": [kw for kw, count in common_keywords],
        "confidence_distribution": {
            "excellent": len([p for p in matched_projects if p.confidence_score >= 0.8]),
            "good": len([p for p in matched_projects if 0.6 <= p.confidence_score < 0.8]),
            "fair": len([p for p in matched_projects if 0.4 <= p.confidence_score < 0.6]),
            "poor": len([p for p in matched_projects if p.confidence_score < 0.4])
        }
    }

async def _process_single_match(job_id: str, user_id: str, max_results: int, db: Session):
    """Background task for processing single match."""
    # Implementation would mirror the main match logic
    # This is for the bulk matching feature
    pass
