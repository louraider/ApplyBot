#Central place to keep all config (database, Redis, logging, API keys, etc.) → avoids hardcoding.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

from app.core.config import settings

# Create database engine
engine=create_engine(
    settings.getDatabaseUrl,
    pool_pre_ping=True,  # Verify connections before use
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base=declarative_base()


def get_db():
    """
    Dependency to get database session.
    Use this in FastAPI endpoints with Depends(get_db).
    """
    db=SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")