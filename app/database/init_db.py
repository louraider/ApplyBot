#database initialization & connection checks.
from sqlalchemy import text
from loguru import logger

from app.database.base import engine, SessionLocal
from app.models import *  # Import all models to register them


def createDatabaseIfNotExists():
    logger.info("Using Supabase - database already exists and ready to use")


def init_db():
    #initialising the structure we are going to use
    try:
        logger.info("Initializing database...")
        
        # Import all models to ensure they are registered
        from app.models import User, Project, Job, Application
        
        # Create all tables
        from app.database.base import Base
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        
        # Check if RLS is enabled (informational)
        try:
            db = SessionLocal()
            result = db.execute(text("""
                SELECT tablename, rowsecurity 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN ('users', 'projects', 'jobs', 'applications')
            """))
            
            rls_status = result.fetchall()
            logger.info("Row-Level Security status:")
            for table, rls_enabled in rls_status:
                status = "✅ Enabled" if rls_enabled else "❌ Disabled"
                logger.info(f"  {table}: {status}")
            
            if not all(rls for _, rls in rls_status):
                logger.warning("⚠️  Some tables don't have RLS enabled!")
                logger.info("Run the SQL script: supabase_security_setup.sql")
            
            db.close()
        except Exception as e:
            logger.warning(f"Could not check RLS status: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


def check_db_connection():
    """Check if database connection is working."""
    try:
        db = SessionLocal()
        # Try a simple query
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Run database initialization
    createDatabaseIfNotExists()
    init_db()