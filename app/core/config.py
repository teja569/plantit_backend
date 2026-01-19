from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Optional, Union
import os
import json
import sys


class Settings(BaseSettings):
    # Core settings
    debug: bool = False
    enable_docs: bool = False  # Enable API docs in production (set ENABLE_DOCS=True)
    secret_key: str = "change-me-in-production"  # Default for development
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    # Priority: POSTGRES_PRISMA_URL > PRISMA_DATABASE_URL > POSTGRES_URL > DATABASE_URL
    # POSTGRES_PRISMA_URL is Supabase's pooled connection (best for serverless)
    database_url: str = "sqlite:///./test.db"  # Default for development
    
    @field_validator('database_url', mode='before')
    @classmethod
    def normalize_database_url(cls, v):
        """Normalize database URL - prefer pooled connections for serverless environments"""
        # Priority order for database URLs
        # 1. POSTGRES_PRISMA_URL (Supabase pooled connection - best for serverless)
        postgres_prisma = os.getenv("POSTGRES_PRISMA_URL")
        if postgres_prisma:
            v = postgres_prisma
        # 2. PRISMA_DATABASE_URL (Generic Prisma pooled connection)
        elif os.getenv("PRISMA_DATABASE_URL"):
            v = os.getenv("PRISMA_DATABASE_URL")
        # 3. POSTGRES_URL (Supabase direct connection with pooler)
        elif os.getenv("POSTGRES_URL"):
            v = os.getenv("POSTGRES_URL")
        # 4. DATABASE_URL (Generic fallback)
        elif not v or v == "sqlite:///./test.db":
            env_url = os.getenv("DATABASE_URL")
            if env_url:
                v = env_url
        
        if isinstance(v, str) and v.startswith('postgres://'):
            # SQLAlchemy 2.0+ requires postgresql:// instead of postgres://
            # Preserve query parameters (like sslmode=require)
            url = v.replace('postgres://', 'postgresql://', 1)
            # Ensure sslmode=require for Supabase and Prisma databases if not already present
            if ('supabase.co' in url or 'db.prisma.io' in url) and 'sslmode=' not in url:
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
    
    # ML Model Configuration
    model_confidence_threshold: float = 0.7
    
    # Supabase Configuration (optional - for direct API usage)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Email
    sendgrid_api_key: Optional[str] = None
    from_email: str = "noreply@plantdelivery.com"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # CORS - stored as string to avoid JSON parsing issues
    allowed_origins: Union[str, None] = Field(
        default="http://localhost:3000,http://localhost:8080,https://admin-panel-pink-nine.vercel.app,https://admin-panel-git-main-prasads-projects-514b962a.vercel.app",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Frontend URL (optional)
    frontend_url: Optional[str] = None
    
    # Vercel
    vercel_url: Optional[str] = None
    
    # AWS
    aws_environment: Optional[str] = None  # Set to "production" when running on AWS
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse comma-separated string - return as string"""
        # Handle None or empty string
        if v is None or (isinstance(v, str) and not v.strip()):
            return "http://localhost:3000,http://localhost:8080"
        # Handle list (if passed programmatically)
        if isinstance(v, list):
            return ','.join(str(item) for item in v)
        # Handle string
        return str(v).strip()
    
    def get_allowed_origins_list(self) -> List[str]:
        """Get allowed_origins as a list"""
        # Handle None or empty
        if not self.allowed_origins:
            return ["http://localhost:3000", "http://localhost:8080"]
        # If "*" is specified, allow all origins (useful for mobile apps)
        if self.allowed_origins.strip() == "*":
            return ["*"]
        # Split by comma and strip whitespace
        return [origin.strip() for origin in self.allowed_origins.split(',') if origin.strip()]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        # Don't parse complex types from env - handle manually
        env_parse_none_str=None,
        # Allow fields starting with 'model_' without warnings
        protected_namespaces=(),
    )


# Initialize settings with validation
try:
    print("[*] Initializing settings...", flush=True)
    settings = Settings()
    
    # Validate required settings in production
    # Render sets RENDER environment variable, or check for production indicators
    is_production = (
        os.getenv("RENDER") is not None or 
        os.getenv("VERCEL") is not None or 
        os.getenv("AWS_EXECUTION_ENV") is not None or
        os.getenv("ENVIRONMENT", "").lower() == "production"
    )
    is_debug = os.getenv("DEBUG", "").lower() == "true"
    
    # Log environment info for debugging (always print, flush immediately)
    print(f"[*] Environment check:", flush=True)
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
        print("[*] Running production validation...", flush=True)
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
            error_msg = "\n".join(f"[ERROR] {e}" for e in errors)
            print(error_msg, file=sys.stderr, flush=True)
            print(error_msg, flush=True)  # Also to stdout
            raise ValueError("\n" + error_msg)
        
        if not settings.gemini_api_key:
            import warnings
            warnings.warn(
                "[WARNING] GEMINI_API_KEY not set - plant identification will not work. "
                "Set GEMINI_API_KEY in Vercel environment variables."
            )
        print("[OK] Production validation passed", flush=True)
    else:
        # Development warnings
        print("[*] Development mode - using warnings instead of errors", flush=True)
        if settings.secret_key == "change-me-in-production":
            import warnings
            warnings.warn("SECRET_KEY is using default value! Set SECRET_KEY environment variable in production.")
        if settings.database_url == "sqlite:///./test.db":
            import warnings
            warnings.warn("DATABASE_URL is using default SQLite! Set DATABASE_URL environment variable in production.")
    
    print("[OK] Settings initialized successfully", flush=True)
    
except Exception as e:
    import sys
    import traceback
    error_msg = f"[ERROR] Error initializing settings: {type(e).__name__}: {str(e)}"
    
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
