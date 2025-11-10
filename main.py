from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from datetime import datetime
import os
import traceback

# Import with better error handling and flushing for Vercel logs
try:
    print("📦 Loading config...", flush=True)
    from app.core.config import settings
    print("✅ Config loaded", flush=True)
except Exception as e:
    import traceback
    print(f"❌ Failed to load config: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    raise

try:
    print("📦 Loading database config...", flush=True)
    from app.core.database import engine, Base
    print("✅ Database config loaded", flush=True)
except Exception as e:
    import traceback
    print(f"❌ Failed to load database config: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    raise

try:
    print("📦 Configuring logging...", flush=True)
    from app.core.logging import logger
    print("✅ Logging configured", flush=True)
except Exception as e:
    import traceback
    print(f"❌ Failed to configure logging: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    raise

try:
    print("📦 Loading API routes...", flush=True)
    from app.api import auth, users, plants, orders, delivery, admin, seller, cart, payments, reviews, categories, notifications
    print("✅ API routes loaded", flush=True)
except Exception as e:
    import traceback
    print(f"❌ Failed to load API routes: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    raise


# Rate limiting - disable in serverless if needed
try:
    limiter = Limiter(key_func=get_remote_address)
except Exception as e:
    # Use print instead of logger since logger might not be initialized yet
    print(f"⚠️ Rate limiter initialization failed: {e}. Continuing without rate limiting.", flush=True)
    limiter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Plant Delivery API...")
    logger.info(f"Environment: {'Production' if not settings.debug else 'Development'}")
    logger.info(f"Render: {os.getenv('RENDER', 'False')}")
    logger.info(f"Vercel: {os.getenv('VERCEL', 'False')}")
    
    # Only create tables in development or if explicitly enabled
    # In production, use migrations (alembic)
    if settings.debug or os.getenv("CREATE_TABLES", "false").lower() == "true":
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Plant Delivery API...")


# Create FastAPI app
app = FastAPI(
    title="Plant Delivery API",
    description="A production-ready FastAPI backend for Plant Delivery Mobile App with AI-powered plant detection",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,  # Disable redoc in production
    lifespan=lifespan
)

# Add rate limiting (if available)
if limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware - configure for production
# Render provides proper host headers, so we can use this in production
if os.getenv("RENDER") is not None:
    # On Render, allow the service hostname
    render_service_url = os.getenv("RENDER_SERVICE_URL", "")
    allowed_hosts = ["*"] if not render_service_url else [render_service_url.replace("https://", "").replace("http://", "")]
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )
elif os.getenv("VERCEL") is None:
    # Local development - allow all
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]
    )


# Include routers
app.include_router(auth, prefix="/api/v1")
app.include_router(users, prefix="/api/v1")
app.include_router(plants, prefix="/api/v1")
app.include_router(orders, prefix="/api/v1")
app.include_router(delivery, prefix="/api/v1")
app.include_router(admin, prefix="/api/v1")
app.include_router(seller, prefix="/api/v1")
app.include_router(cart, prefix="/api/v1")
app.include_router(payments, prefix="/api/v1")
app.include_router(reviews, prefix="/api/v1")
app.include_router(categories, prefix="/api/v1")
app.include_router(notifications, prefix="/api/v1")


# Global exception handlers - production-ready error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()} - Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred" if not settings.debug else str(exc),
            "path": str(request.url.path)
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Plant Delivery API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else None,
        "redoc": "/redoc" if settings.debug else None,
        "environment": "production" if not settings.debug else "development"
    }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon - returns 204 No Content"""
    # Return 204 No Content - browsers will handle missing favicon gracefully
    # This prevents 500 errors for favicon requests
    return Response(status_code=204)


@app.get("/favicon.png")
async def favicon_png():
    """Serve favicon as PNG (alternative)"""
    # Minimal transparent PNG (1x1 pixel)
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
        0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
        0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49,
        0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ])
    
    return Response(
        content=png_data,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=31536000"  # Cache for 1 year
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for production monitoring"""
    import time
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "environment": "production" if not settings.debug else "development",
        "render": os.getenv("RENDER") is not None,
        "vercel": os.getenv("VERCEL") is not None
    }
    
    # Test database connection
    try:
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"
    
    # Check Gemini API (non-blocking)
    try:
        from app.services.ml_service import plant_classifier
        if plant_classifier._initialized:
            health_status["gemini"] = "ready"
        else:
            health_status["gemini"] = "not_configured"
    except Exception:
        health_status["gemini"] = "unknown"
    
    # Response time
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


if __name__ == "__main__":
    import uvicorn
    # Use string for reload to work properly, but disable reload if it causes issues
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level="info"
        )
    except AttributeError as e:
        # Fallback: run without reload if there's a compatibility issue
        import sys
        if "--reload" in sys.argv or settings.debug:
            print("Warning: Reload mode has compatibility issues. Running without reload.")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
