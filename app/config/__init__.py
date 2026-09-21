"""Configuration package for SCU Schedule Generator."""

from app.config.feature_flags import FeatureFlags, get_feature_flags
from app.config.settings import Settings, get_settings

__all__ = [
    "Settings",
    "get_settings",
    "FeatureFlags",
    "get_feature_flags",
]
