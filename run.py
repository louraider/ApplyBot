import uvicorn
from loguru import logger

if __name__ == "__main__":
    logger.info("🚀 Starting Job Application System development server...")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,  # Use loguru instead of uvicorn's logging
        access_log=False  # Disable uvicorn access logs, use our structured logging
    )