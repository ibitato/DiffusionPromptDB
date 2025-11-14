"""
API Configuration

Configuration settings for the FastAPI application.
"""

from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    # API Info
    app_name: str = "DiffusionPromptDB API"
    app_version: str = "1.0.0"
    app_description: str = (
        "REST API for Stable Diffusion Prompt Database and Catalogation"
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False  # Set to True for development, False for production

    # Database (unified - catalog DB with 10,386 prompts, located in api/database/)
    prompts_db_path: str = "database/prompts_catalog.db"
    catalog_db_path: str = "database/prompts_catalog.db"
    users_db_path: str = "../data/users.db"

    # Security
    api_keys: List[str] = ["REDACTED_API_KEY"]  # Change in production!
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",  # Vite alternative port
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",  # Vite alternative
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Logging
    log_level: str = "INFO"
    log_file: str = "api.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
