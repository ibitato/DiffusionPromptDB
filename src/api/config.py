"""
API Configuration

Configuration settings for the FastAPI application.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path
from pydantic import EmailStr, Field, field_validator

BASE_DIR = Path(__file__).resolve().parents[2]


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
    prompts_db_path: str = str(BASE_DIR / "database/prompts_catalog.db")
    catalog_db_path: str = str(BASE_DIR / "database/prompts_catalog.db")
    users_db_path: str = str(BASE_DIR / "data/users.db")

    # Security
    api_keys: List[str] = Field(default_factory=list)
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Email / SMTP
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_sender: Optional[EmailStr] = None
    smtp_use_tls: bool = True
    email_debug_mode: bool = True  # When true, include tokens in API responses for dev
    public_app_url: str = "https://www.diffusionprompt.net"

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

    # Media / ingestion
    media_root: str = str(BASE_DIR / "media")
    media_thumbnails_subdir: str = "thumbnails"
    thumbnail_max_size: int = 512
    ingestion_default_tags: List[str] = Field(default_factory=list)

    # Logging
    log_level: str = "INFO"
    log_file: str = "api.log"
    password_rotation_days: int = 90
    password_min_length: int = 12
    password_history_limit: int = 5

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        if not value or value == "your-secret-key-change-this-in-production":
            raise ValueError(
                "JWT secret key must be provided via the JWT_SECRET_KEY environment variable."
            )
        return value

    @field_validator("api_keys")
    @classmethod
    def validate_api_keys(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError(
                "API_KEYS environment variable must define at least one API key."
            )
        return value

    @field_validator("thumbnail_max_size")
    @classmethod
    def validate_thumbnail_size(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("thumbnail_max_size must be greater than zero.")
        return value

    @field_validator("ingestion_default_tags", mode="before")
    @classmethod
    def parse_default_tags(cls, value):
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(",") if tag.strip()]
        return value

    @field_validator("smtp_port")
    @classmethod
    def validate_smtp_port(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("SMTP port must be greater than zero.")
        return value

    @field_validator(
        "prompts_db_path", "catalog_db_path", "users_db_path", "media_root", mode="before"
    )
    @classmethod
    def resolve_relative_paths(cls, value: str | Path) -> str:
        path = Path(value)
        if not path.is_absolute():
            path = BASE_DIR / path
        return str(path)

    @field_validator("smtp_host", "smtp_username", "smtp_password", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("smtp_sender", mode="before")
    @classmethod
    def validate_smtp_config(cls, value, values):
        if isinstance(value, str) and not value.strip():
            value = None
        host = values.data.get("smtp_host")
        username = values.data.get("smtp_username")
        password = values.data.get("smtp_password")

        if any([host, username, password, value]):
            missing = [
                name
                for name, present in [
                    ("smtp_host", bool(host)),
                    ("smtp_username", bool(username)),
                    ("smtp_password", bool(password)),
                    ("smtp_sender", bool(value)),
                ]
                if not present
            ]
            if missing:
                raise ValueError(
                    "SMTP configuration incomplete: missing "
                    + ", ".join(missing)
                    + ". Provide all SMTP_* variables or none."
                )
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
