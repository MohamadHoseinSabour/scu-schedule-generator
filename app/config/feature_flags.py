"""Feature flags configuration module.

Controls feature toggles across the application loaded from environment variables.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureFlags(BaseSettings):
    """Feature toggle configuration flags."""

    PORTAL_ENABLED: bool = False
    ADMIN_ENABLED: bool = True
    REFERRAL_ENABLED: bool = True
    IMAGE_EXPORT_ENABLED: bool = True
    HTML_EXPORT_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_feature_flags() -> FeatureFlags:
    """Return a cached instance of feature flags."""
    return FeatureFlags()
