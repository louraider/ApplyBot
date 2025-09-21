#!/usr/bin/env python3
"""
Load test jobs into Supabase for development and testing.
"""

import asyncio
from loguru import logger
from app.database.base import SessionLocal
from app.services.job_service import JobService


async def load_jobs_for_testing():
    """Load a variety of jobs for testing purposes."""
    logger.info("🚀 Loading test jobs into Supabase...")
    
    # Different keyword sets to get variety
    keyword_sets = [
        ["python", "django", "fastapi"],
        ["javascript", "react", "node.js"],
        ["java", "spring", "backend"],
        ["frontend", "vue", "angular"],
        ["fullstack", "full-stack", "mern"],
        ["devops", "kubernetes", "docker"],
        ["data", "machine learning", "ai"],
        ["mobile", "react native", "flutter"],
        ["golang", "go", "microservices"],
        ["rust", "systems", "performance"]
    ]
    
    db = SessionLocal()
    job_service = JobService(db)
    
    total_new_jobs = 0
    total_fetched = 0
    
    try:
        for i, keywords in enumerate(keyword_sets, 1):
            logger.info(f"Batch {i}/{len(keyword_sets)}: Fetching {keywords}")
            
            try:
                results = await job_service.fetch_and_store_jobs(
                    keywords=keywords,
                    limit_per_source=20  # 20 jobs per source per keyword set
                )
                
                batch_new = results["new_jobs"]
                batch_total = results["total_fetched"]
                
                total_new_jobs += batch_new
                total_fetched += batch_total
                
                logger.info(f"Batch {i} complete: {batch_new} new jobs, {batch_total} total fetched")
                
                # Small delay to be respectful to APIs
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Batch {i} failed: {e}")
                continue
        
        # Final statistics
        stats = job_service.get_job_statistics()
        
        logger.info("")
        logger.info("🎉 Job loading complete!")
        logger.info(f"📊 Results:")
        logger.info(f"  - Total fetched this session: {total_fetched}")
        logger.info(f"  - New jobs added: {total_new_jobs}")
        logger.info(f"  - Total jobs in database: {stats['total_jobs']}")
        logger.info(f"  - Jobs by source: {stats['jobs_by_source']}")
        logger.info("")
        logger.info("🔍 View your jobs:")
        logger.info("  - Supabase Dashboard > Table Editor > jobs")
        logger.info("  - API: GET /api/v1/jobs/?limit=50")
        logger.info("  - Search: GET /api/v1/jobs/?keywords=python&limit=10")
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(load_jobs_for_testing())