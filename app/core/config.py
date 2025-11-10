from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Optional
import os
import json
import sys


class Settings(BaseSettings):
    # Core settings
    debug: bool = False
    secret_key: str = "change-me-in-production"  # Default for development
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    # For Prisma Postgres: Use PRISMA_DATABASE_URL (includes connection pooling) for serverless
    # Falls back to DATABASE_URL if PRISMA_DATABASE_URL is not set
    database_url: str = "sqlite:///./test.db"  # Default for development
    
    @field_validator('database_url', mode='before')
    @classmethod
    def normalize_database_url(cls, v):
        """Normalize database URL - prefer PRISMA_DATABASE_URL, convert postgres:// to postgresql://"""
        # Prefer PRISMA_DATABASE_URL for serverless (includes connection pooling)
        prisma_url = os.getenv("PRISMA_DATABASE_URL")
        if prisma_url:
            v = prisma_url
        elif not v or v == "sqlite:///./test.db":
            # Fall back to DATABASE_URL if PRISMA_DATABASE_URL not set
            env_url = os.getenv("DATABASE_URL")
            if env_url:
                v = env_url
        
        if isinstance(v, str) and v.startswith('postgres://'):
            # SQLAlchemy 2.0+ requires postgresql:// instead of postgres://
            # Preserve query parameters (like sslmode=require for Prisma)
            url = v.replace('postgres://', 'postgresql://', 1)
            # Ensure sslmode=require for Prisma databases if not already present
            if 'db.prisma.io' in url and 'sslmode=' not in url:
                separator = '&' if '?' in url else '?'
                url = f"{url}{separator}sslmode=require"
            return url
        return v
    
    # Cloud Storage
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_bucket_name: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # Cloudinary
    cloudinary_cloud_name: Optional[str] = None
    cloudinary_api_key: Optional[str] = None
    cloudinary_api_secret: Optional[str] = None
    
    # Google Gemini API
    gemini_api_key: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Email
    sendgrid_api_key: Optional[str] = None
    from_email: str = "noreply@plantdelivery.com"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # CORS - stored as string to avoid JSON parsing issues
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Frontend URL (optional)
    frontend_url: Optional[str] = None
    
    # Vercel
    vercel_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse comma-separated string - return as string"""
        if v is None:
            return "http://localhost:3000,http://localhost:8080"
        if isinstance(v, list):
            return ','.join(v)
        return str(v)
    
    def get_allowed_origins_list(self) -> List[str]:
        """Get allowed_origins as a list"""
        # Split by comma and strip whitespace
        return [origin.strip() for origin in self.allowed_origins.split(',') if origin.strip()]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        # Don't parse complex types from env - handle manually
        env_parse_none_str=None,
    )


# Initialize settings with validation
try:
    print("📋 Initializing settings...", flush=True)
    settings = Settings()
    
    # Validate required settings in production
    # Render sets RENDER environment variable, or check for production indicators
    is_production = os.getenv("RENDER") is not None or os.getenv("VERCEL") is not None
    is_debug = os.getenv("DEBUG", "").lower() == "true"
    
    # Log environment info for debugging (always print, flush immediately)
    print(f"🔍 Environment check:", flush=True)
    print(f"   RENDER={os.getenv('RENDER', 'not set')}", flush=True)
    print(f"   VERCEL={os.getenv('VERCEL', 'not set')}", flush=True)
    print(f"   DEBUG={os.getenv('DEBUG', 'not set')}", flush=True)
    print(f"   is_production={is_production}", flush=True)
    print(f"   is_debug={is_debug}", flush=True)
    print(f"   SECRET_KEY set: {settings.secret_key != 'change-me-in-production'}", flush=True)
    print(f"   SECRET_KEY value: {settings.secret_key[:20] + '...' if len(settings.secret_key) > 20 else settings.secret_key}", flush=True)
    print(f"   DATABASE_URL set: {settings.database_url != 'sqlite:///./test.db'}", flush=True)
    print(f"   DATABASE_URL preview: {settings.database_url[:50] + '...' if len(settings.database_url) > 50 else settings.database_url}", flush=True)
    print(f"   GEMINI_API_KEY set: {bool(settings.gemini_api_key)}", flush=True)
    
    if is_production and not is_debug:
        # Production validation - stricter checks
        print("🔍 Running production validation...", flush=True)
        errors = []
        
        if settings.secret_key == "change-me-in-production":
            errors.append(
                "SECRET_KEY must be set in production! "
                "Set SECRET_KEY environment variable in Vercel."
            )
        
        if settings.database_url == "sqlite:///./test.db":
            errors.append(
                "DATABASE_URL must be set in production! "
                "Use PostgreSQL connection string in Vercel environment variables."
            )
        
        if errors:
            error_msg = "\n".join(f"❌ {e}" for e in errors)
            print(error_msg, file=sys.stderr, flush=True)
            print(error_msg, flush=True)  # Also to stdout
            raise ValueError("\n" + error_msg)
        
        if not settings.gemini_api_key:
            import warnings
            warnings.warn(
                "⚠️ GEMINI_API_KEY not set - plant identification will not work. "
                "Set GEMINI_API_KEY in Vercel environment variables."
            )
        print("✅ Production validation passed", flush=True)
    else:
        # Development warnings
        print("🔍 Development mode - using warnings instead of errors", flush=True)
        if settings.secret_key == "change-me-in-production":
            import warnings
            warnings.warn("SECRET_KEY is using default value! Set SECRET_KEY environment variable in production.")
        if settings.database_url == "sqlite:///./test.db":
            import warnings
            warnings.warn("DATABASE_URL is using default SQLite! Set DATABASE_URL environment variable in production.")
    
    print("✅ Settings initialized successfully", flush=True)
    
except Exception as e:
    import sys
    import traceback
    error_msg = f"❌ Error initializing settings: {type(e).__name__}: {str(e)}"
    
    # Print to both streams with flushing
    for stream in [sys.stdout, sys.stderr]:
        print(error_msg, file=stream, flush=True)
        print("\n" + "="*60, file=stream, flush=True)
        print("SETTINGS INITIALIZATION TRACEBACK:", file=stream, flush=True)
        print("="*60, file=stream, flush=True)
        traceback.print_exc(file=stream)
        print("="*60, file=stream, flush=True)
    raise

# Post-initialization: Configure CORS origins for Vercel
if os.getenv("VERCEL") is not None:
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        # Add Vercel URL to allowed origins
        current_origins = settings.get_allowed_origins_list()
        if f"https://{vercel_url}" not in current_origins:
            new_origins = current_origins + [f"https://{vercel_url}"]
            settings.allowed_origins = ','.join(new_origins)
    # Add common production origins
    if os.getenv("FRONTEND_URL"):
        frontend_url = os.getenv("FRONTEND_URL")
        current_origins = settings.get_allowed_origins_list()
        if frontend_url not in current_origins:
            new_origins = current_origins + [frontend_url]
            settings.allowed_origins = ','.join(new_origins)
