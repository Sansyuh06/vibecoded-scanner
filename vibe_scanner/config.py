from typing import Any, Dict, Optional
from pydantic import Field, SecretStr, AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    PROJECT_NAME: str = "Vibe Scanner"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    
    # Security: Use environment variables - NEVER hardcode secrets
    SECRET_KEY: SecretStr = Field(
        description="Encryption key for tokens. Min 32 chars. Generate: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )
    
    # Token expiration - shorter lived tokens (15 min access, 7 day refresh)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="Access token expiration in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")
    
    # Database configuration
    DATABASE_URL: AnyUrl = Field(
        default="sqlite+aiosqlite:///./vibe.db",
        description="Database URL. Production: postgresql+asyncpg://user:pass@host:5432/db"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Celery async tasks
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # API Security
    API_RATE_LIMIT: str = Field(default="5/minute", description="Rate limit for API endpoints")
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Scanner configuration
    MAX_PAGES_TO_CRAWL: int = Field(default=500, description="Maximum pages to crawl per scan")
    CRAWLER_TIMEOUT: float = Field(default=10.0, description="HTTP request timeout in seconds")
    CRAWLER_CONCURRENCY: int = Field(default=10, description="Concurrent requests during crawling")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")

    @field_validator("CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def set_celery_defaults(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        return info.data.get("REDIS_URL")

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v):
        if isinstance(v, str) and len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def validate_environment(cls, v):
        valid_envs = {"development", "staging", "production"}
        if v not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of {valid_envs}")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        validate_default=True,
    )


# Load settings at startup
try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load settings: {e}")
    raise
