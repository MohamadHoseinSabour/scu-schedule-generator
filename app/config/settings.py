"""Application configuration settings module.

Loads environment variables using Pydantic Settings and validates system settings.
"""

from functools import lru_cache
from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings loaded from environment variables and .env file."""

    # Telegram Bot Configuration
    BOT_TOKEN: str = ""
    BOT_USERNAME: str = ""
    ADMIN_TELEGRAM_IDS: list[int] = []

    # Database & Storage
    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/scu_schedule.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    STORAGE_PATH: str = "./storage"

    # Application Limits & Lifecycle
    MAX_FILE_SIZE_MB: int = 10
    OUTPUT_TTL_HOURS: int = 24
    RATE_LIMIT_FILES: int = 5
    RATE_LIMIT_WINDOW_MINUTES: int = 10

    # Runtime Environment & Flags
    APP_ENV: str = "development"
    PARSER_DEBUG: bool = False
    TEMPLATE_VERSION: str = "1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("ADMIN_TELEGRAM_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: Any) -> list[int]:
        """Normalize ADMIN_TELEGRAM_IDS from int, comma-separated string, or list."""
        if value is None or value == "":
            return []
        if isinstance(value, (int, float)):
            return [int(value)]
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                value = value[1:-1].strip()
            if not value:
                return []
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        if isinstance(value, (list, tuple, set)):
            return [int(item) for item in value]
        return []

    @property
    def is_production(self) -> bool:
        """Check if application is running in production mode."""
        return self.APP_ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if application is running in development mode."""
        return self.APP_ENV.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of the application settings."""
    return Settings()
