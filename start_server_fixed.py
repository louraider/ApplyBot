#!/usr/bin/env python3
"""
Fixed server startup script.
"""

import uvicorn
from loguru import logger

def main():
    logger.info("🚀 Starting Job Application System API server...")
    logger.info("📋 Available endpoints:")
    logger.info("  - API Documentation: http://localhost:8000/docs")
    logger.info("  - Alternative Docs: http://localhost:8000/redoc")
    logger.info("  - Health Check: http://localhost:8000/health")
    logger.info("  - Root: http://localhost:8000/")
    logger.info("")
    logger.info("📮 Import postman_collection.json into Postman to test all endpoints")
    logger.info("🛑 Press Ctrl+C to stop the server")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid the import string error
        log_level="info"
    )

if __name__ == "__main__":
    main()