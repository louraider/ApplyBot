#config information
import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    #appplication settings
    
    # Basic app settings
    PROJECT_NAME:str=os.getenv("PROJECT_NAME", "ApplyBot")
    ENVIRONMENT:str=os.getenv("ENVIRONMENT", "development")
    DEBUG:bool=os.getenv("DEBUG", "true").lower() == "true"
    API_V1_STR:str="/api/v1"
    
    # CORS settings
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        #here we are defining which url's from the froentend can call the backend
        origins=os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000, http://localhost:8000")
        return [origin.strip() for origin in origins.split(",")]
    
    # SUPABASE INFORMATION
    DATABASE_URL:str=os.getenv("DATABASE_URL", "")
    SUPABASE_URL:str=os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY:str=os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY:str=os.getenv("SUPABASE_SERVICE_KEY", "")
    
    @property
    def getDatabaseUrl(self) -> str:
        #will look for it in the en file 
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is required. Please set up your Supabase credentials in .env file.")
        return self.DATABASE_URL
    
    # Redis settings (for future caching and task queue)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # External API settings
    REMOTEOK_API_URL: str = "https://remoteok.io/api"
    
    # AI Service settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # File storage settings
    UPLOAD_DIR: str = "uploads"
    RESUME_DIR: str = "uploads/resumes"
    COVER_LETTER_DIR: str = "uploads/cover_letters"
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"


# Create global settings instance
settings = Settings()