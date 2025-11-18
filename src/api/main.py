"""
FastAPI Application - DiffusionPromptDB API

Main API application for DiffusionPromptDB.
Provides RESTful API endpoints for managing Stable Diffusion prompts.

Features:
    - JWT Authentication with role-based access control
    - CRUD operations for prompts management
    - Advanced search and filtering capabilities
    - Rate limiting to prevent abuse
    - CORS support for frontend integration
    - Comprehensive error handling
    - Auto-generated documentation (Swagger/ReDoc)
    - Health monitoring endpoints
    - User preferences management

Author: ibitato (REDACTED_EMAIL)
License: Apache 2.0
Version: 1.0.0
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime
import os
from pathlib import Path

from .config import settings
from .routers import prompts, catalog, search, admin, auth, preferences, profile, admin_users
from .middleware.security import add_security_headers

# Configure logging with file and console handlers
# Log level and format are controlled via settings
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(settings.log_file), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Initialize rate limiter with IP-based limiting
# Default: 100 requests/minute, 1000 requests/hour
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application instance with metadata
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc",  # ReDoc documentation
    openapi_url="/openapi.json",  # OpenAPI schema
)

# Configure rate limiting middleware
# Prevents API abuse and ensures fair usage
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS middleware for frontend integration
# Allows cross-origin requests from specified origins
# CORS is configured via environment variables for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Configured for www.diffusionprompt.net
    allow_credentials=settings.cors_allow_credentials,  # Allow cookies/auth headers
    allow_methods=settings.cors_allow_methods,  # Allowed HTTP methods
    allow_headers=settings.cors_allow_headers,  # Allowed request headers
)

# Serve media files (thumbnails) under /media
media_directory = Path(settings.media_root).expanduser()
media_directory.mkdir(parents=True, exist_ok=True)
app.mount(
    "/media",
    StaticFiles(directory=str(media_directory)),
    name="media",
)


# Add security headers middleware
# Implements OWASP recommended security headers
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Apply security headers to all responses."""
    return await add_security_headers(request, call_next)


# Register API routers with versioned prefixes
# Each router handles a specific domain of the application
app.include_router(
    auth.router, prefix="/api/v1/auth", tags=["auth"]
)  # Authentication endpoints
app.include_router(
    prompts.router, prefix="/api/v1/prompts", tags=["prompts"]
)  # Prompt CRUD operations
app.include_router(
    catalog.router, prefix="/api/v1/catalog", tags=["catalog"]
)  # Catalog browsing
app.include_router(
    search.router, prefix="/api/v1/search", tags=["search"]
)  # Search functionality
app.include_router(
    admin.router, prefix="/api/v1/admin", tags=["admin"]
)  # Admin operations
app.include_router(
    admin_users.router, prefix="/api/v1/admin", tags=["admin"]
)
app.include_router(
    preferences.router, prefix="/api/v1/user", tags=["user"]
)  # User preferences
app.include_router(
    profile.router, prefix="/api/v1/user", tags=["user"]
)


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing API information and navigation.

    Returns:
        dict: API metadata including name, version, and available endpoints

    Example Response:
        {
            "name": "DiffusionPromptDB API",
            "version": "1.0.0",
            "description": "API for managing Stable Diffusion prompts",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/admin/health"
        }
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/admin/health",
    }


@app.get("/api/v1/health", tags=["monitoring"])
@limiter.limit("10/minute")
async def health_check(request: Request):
    """
    Health check endpoint for monitoring API status.

    Args:
        request (Request): FastAPI request object (required for rate limiting)

    Returns:
        dict: Health status, timestamp, and environment

    Rate Limit:
        10 requests per minute (to prevent abuse)

    Example Response:
        {
            "status": "healthy",
            "timestamp": "2024-11-14T12:00:00.000000"
        }
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": settings.app_version,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Catches all unhandled exceptions, logs them for debugging,
    and returns a generic error response to prevent information leakage.

    Args:
        request (Request): The request that caused the exception
        exc (Exception): The unhandled exception

    Returns:
        JSONResponse: Generic error response with 500 status code

    Side Effects:
        - Logs full exception details to application logs
        - Increments error metrics (if configured)
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    """
    Development server entry point.

    Starts the Uvicorn ASGI server with hot-reload for development.
    For production, use: uvicorn src.api.main:app --host 0.0.0.0 --port 8000

    Server Configuration:
        - Host: Configured via settings (default: 0.0.0.0)
        - Port: Configured via settings (default: 8000)
        - Reload: Auto-reload on code changes in development
        - Log Level: Configured via settings (default: INFO)
    """
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
