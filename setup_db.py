#!/usr/bin/env python3
"""
Database setup script for development.
"""

import sys
from loguru import logger

def main():
    """Set up the Supabase database for development."""
    logger.info("🗄️Setting up Supabase database for Job Application System...")
    
    try:
        from app.core.config import settings
        from app.database.init_db import create_database_if_not_exists, init_db, check_db_connection
        
        # Verify Supabase configuration
        if not settings.DATABASE_URL:
            logger.error("❌ DATABASE_URL not configured!")
            logger.info("Please set up your Supabase credentials:")
            logger.info("  1. Manually edit .env file with your Supabase details")
            logger.info("  2. See SUPABASE_SETUP.md for detailed instructions")
            return False
        
        logger.info("✅ Supabase configuration detected")
        
        # Step 1: Database already exists in Supabase
        logger.info("Step 1: Verifying Supabase database...")
        create_database_if_not_exists()
        
        # Step 2: Check connection
        logger.info("Step 2: Testing Supabase connection...")
        if not check_db_connection():
            logger.error("❌ Supabase connection failed!")
            logger.info("Troubleshooting:")
            logger.info("  1. Check your DATABASE_URL in .env")
            logger.info("  2. Verify Supabase project is active (not paused)")
            logger.info("  3. Ensure database password is correct")
            logger.info("  4. Check if project reference is correct")
            logger.info("  5. Check SUPABASE_SETUP.md for setup instructions")
            return False
        
        # Step 3: Initialize tables
        logger.info("Step 3: Creating database tables in Supabase...")
        if init_db():
            logger.info("✅ Supabase database setup completed successfully!")
            logger.info("")
            logger.info("📋 Database tables created:")
            logger.info("  - users (for user profiles)")
            logger.info("  - projects (for user projects)")
            logger.info("  - jobs (for job listings)")
            logger.info("  - applications (for tracking applications)")
            logger.info("")
            logger.info("🎉 Supabase is ready!")
            logger.info("  - View tables: Supabase Dashboard > Table Editor")
            logger.info("  - Run queries: Supabase Dashboard > SQL Editor")
            logger.info("  - Monitor usage: Supabase Dashboard > Settings > Usage")
            logger.info("")
            logger.info("🚀 You can now start the API server with: python start_server.py")
            return True
        else:
            logger.error("❌ Database initialization failed!")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("Please install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)