from loguru import logger
import sys
import os
from app.core.config import settings

# Remove default logger
logger.remove()

# Add console logger (works in both local and serverless)
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Add file logger only if not in serverless environment
# Vercel serverless functions don't have persistent file system
# Only enable file logging in non-serverless environments
if os.getenv("VERCEL") is None and os.getenv("RENDER") is None:
    try:
        # Ensure log directory exists
        log_dir = os.path.dirname(settings.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        logger.add(
            settings.log_file,
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="1 day",
            retention="30 days"
        )
    except Exception as e:
        # If file logging fails, continue with console logging only
        logger.warning(f"Failed to set up file logging: {e}")
