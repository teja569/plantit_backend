#!/bin/bash
# Render startup script for FastAPI application

# Set Python to unbuffered mode for better logging
export PYTHONUNBUFFERED=1

# Run database migrations (optional - uncomment if using Alembic)
# alembic upgrade head

# Start the FastAPI application with Uvicorn
# Render provides PORT environment variable
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
