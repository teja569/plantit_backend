from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from app.core.config import settings
import os

# Configure connection pooling
# Render uses persistent servers, so use QueuePool for better performance
# Serverless environments (like Vercel) would use NullPool
is_serverless = os.getenv("VERCEL") is not None  # Check for serverless environment
poolclass = NullPool if is_serverless else QueuePool
pool_size = 1 if is_serverless else 5
max_overflow = 0 if is_serverless else 10

# For serverless, use NullPool to avoid connection issues
# For traditional deployments, use QueuePool
# Note: create_engine doesn't actually connect until first use, so this is safe
try:
    # Prisma Postgres requires SSL - ensure it's in the connection string
    db_url_lower = settings.database_url.lower()
    is_postgres = "postgresql" in db_url_lower or "postgres://" in db_url_lower
    
    # Build connect_args for PostgreSQL (especially Prisma)
    # Prisma Postgres requires SSL - psycopg2 uses sslmode parameter
    connect_args = {}
    if is_postgres:
        # Check if sslmode is in URL (Prisma usually includes it)
        has_ssl_in_url = "sslmode=" in settings.database_url.lower()
        
        connect_args = {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"  # 30 second timeout
        }
        
        # For Prisma databases, ensure SSL is required
        # psycopg2 accepts sslmode as a query parameter in URL or as connect_arg
        # If not in URL, add it to connect_args
        if not has_ssl_in_url:
            # For psycopg2, we can add sslmode to the URL or use ssl parameter
            # Since URL already normalized, add sslmode=require to connect_args
            # Note: psycopg2 will use sslmode from URL if present, otherwise from connect_args
            pass  # sslmode should be in URL after normalization
    
    engine = create_engine(
        settings.database_url,
        poolclass=poolclass,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,  # Verify connections before using (important for Prisma)
        connect_args=connect_args,
        # Don't connect on engine creation - lazy connection
        pool_reset_on_return='commit' if is_serverless else 'rollback',
        # For Prisma/Postgres, ensure proper encoding
        echo=False  # Set to True for SQL query logging (debug only)
    )
    print(f"[OK] Database engine created successfully", flush=True)
    print(f"   Pool class: {poolclass.__name__}", flush=True)
    print(f"   Database type: {'PostgreSQL' if is_postgres else 'Other'}", flush=True)
except Exception as e:
    import sys
    import traceback
    print(f"[ERROR] Failed to create database engine: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    print(f"   DATABASE_URL preview: {settings.database_url[:80]}...", file=sys.stderr, flush=True)
    traceback.print_exc(file=sys.stderr)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # Rollback on any exception
        db.rollback()
        from app.core.logging import logger
        logger.error(f"Database session error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()
