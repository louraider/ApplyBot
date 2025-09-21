#!/usr/bin/env python3
"""
Start the FastAPI development server for testing.
"""

import uvicorn
from loguru import logger
from app.main import app

def main():
    """Start the development server."""
    logger.info("🚀 Starting Job Application System API server...")
    logger.info("📋 Available endpoints:")
    logger.info("  - API Documentation: http://localhost:8000/docs")
    logger.info("  - Alternative Docs: http://localhost:8000/redoc")
    logger.info("  - Health Check: http://localhost:8000/health")
    logger.info("  - Root: http://localhost:8000/")
    logger.info("")
    logger.info("📮 Import postman_collection.json into Postman to test all endpoints")
    logger.info("🛑 Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_config=None,  # Use loguru instead
            access_log=False  # Disable uvicorn access logs
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")

if __name__ == "__main__":
    main()