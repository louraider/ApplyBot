"""
Production configuration and best practices.
"""

import os
from pathlib import Path
from typing import Optional
from loguru import logger


class ProductionConfig:
    """Production configuration management."""
    
    # File storage settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES = {'.pdf', '.txt', '.docx'}
    
    # Generation limits
    MAX_RESUMES_PER_USER_PER_DAY = 50
    MAX_COVER_LETTERS_PER_USER_PER_DAY = 100
    
    # Cleanup settings
    FILE_RETENTION_DAYS = 30
    CLEANUP_INTERVAL_HOURS = 24
    
    # AI settings
    AI_TIMEOUT_SECONDS = 30
    AI_MAX_RETRIES = 2
    
    # Rate limiting
    API_RATE_LIMIT = "100/minute"
    
    @classmethod
    def validate_environment(cls) -> bool:
        """Validate production environment setup."""
        
        issues = []
        
        # Check required directories
        required_dirs = [
            "app/templates",
            "app/generated/resumes", 
            "app/generated/cover_letters"
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                issues.append(f"Missing directory: {dir_path}")
        
        # Check environment variables
        required_env_vars = [
            "DATABASE_URL",
            "SECRET_KEY"
        ]
        
        for env_var in required_env_vars:
            if not os.getenv(env_var):
                issues.append(f"Missing environment variable: {env_var}")
        
        # Check optional but recommended env vars
        optional_env_vars = [
            "GROQ_API_KEY",
            "OPENAI_API_KEY",
            "REED_API_KEY",
            "ADZUNA_APP_ID",
            "ADZUNA_APP_KEY"
        ]
        
        missing_optional = []
        for env_var in optional_env_vars:
            if not os.getenv(env_var) or os.getenv(env_var).startswith("your-"):
                missing_optional.append(env_var)
        
        # Report issues
        if issues:
            logger.error("Production environment validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        
        if missing_optional:
            logger.warning("Optional environment variables not set:")
            for var in missing_optional:
                logger.warning(f"  - {var}")
        
        logger.info("Production environment validation passed")
        return True
    
    @classmethod
    def setup_directories(cls):
        """Create required directories."""
        
        directories = [
            "app/templates",
            "app/generated",
            "app/generated/resumes",
            "app/generated/cover_letters",
            "logs"
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ready: {dir_path}")
    
    @classmethod
    def get_file_limits(cls) -> dict:
        """Get file handling limits."""
        return {
            "max_file_size": cls.MAX_FILE_SIZE,
            "allowed_types": list(cls.ALLOWED_FILE_TYPES),
            "retention_days": cls.FILE_RETENTION_DAYS
        }
    
    @classmethod
    def get_generation_limits(cls) -> dict:
        """Get generation limits."""
        return {
            "max_resumes_per_day": cls.MAX_RESUMES_PER_USER_PER_DAY,
            "max_cover_letters_per_day": cls.MAX_COVER_LETTERS_PER_USER_PER_DAY,
            "ai_timeout": cls.AI_TIMEOUT_SECONDS,
            "ai_retries": cls.AI_MAX_RETRIES
        }


class HealthChecker:
    """System health monitoring."""
    
    @staticmethod
    def check_system_health() -> dict:
        """Comprehensive system health check."""
        
        health_status = {
            "status": "healthy",
            "timestamp": "",
            "services": {},
            "issues": []
        }
        
        from datetime import datetime
        health_status["timestamp"] = datetime.utcnow().isoformat()
        
        # Check database connection
        try:
            from app.database.base import get_db
            next(get_db())
            health_status["services"]["database"] = "healthy"
        except Exception as e:
            health_status["services"]["database"] = "unhealthy"
            health_status["issues"].append(f"Database: {str(e)}")
        
        # Check file system
        try:
            test_file = Path("app/generated/health_check.txt")
            test_file.write_text("health check")
            test_file.unlink()
            health_status["services"]["filesystem"] = "healthy"
        except Exception as e:
            health_status["services"]["filesystem"] = "unhealthy"
            health_status["issues"].append(f"Filesystem: {str(e)}")
        
        # Check AI services
        ai_status = []
        
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and not groq_key.startswith("your-"):
            ai_status.append("groq")
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and not openai_key.startswith("your-"):
            ai_status.append("openai")
        
        health_status["services"]["ai"] = "available" if ai_status else "unavailable"
        if ai_status:
            health_status["services"]["ai_providers"] = ai_status
        
        # Check job sources
        job_sources = []
        
        if os.getenv("REED_API_KEY") and not os.getenv("REED_API_KEY").startswith("YOUR_"):
            job_sources.append("reed")
        
        if (os.getenv("ADZUNA_APP_ID") and os.getenv("ADZUNA_APP_KEY") and 
            not os.getenv("ADZUNA_APP_ID").startswith("YOUR_")):
            job_sources.append("adzuna")
        
        job_sources.extend(["remoteok", "github"])  # Always available
        
        health_status["services"]["job_sources"] = len(job_sources)
        health_status["services"]["active_sources"] = job_sources
        
        # Overall status
        if health_status["issues"]:
            health_status["status"] = "degraded" if len(health_status["issues"]) < 2 else "unhealthy"
        
        return health_status


# Initialize production config
production_config = ProductionConfig()
health_checker = HealthChecker()