"""Tests for configuration settings and feature flags."""

from app.config.feature_flags import FeatureFlags, get_feature_flags
from app.config.settings import Settings, get_settings
from app.domain.models import ScheduleReport


def test_settings_defaults():
    """Verify default settings values."""
    settings = Settings()
    assert settings.MAX_FILE_SIZE_MB == 10
    assert settings.OUTPUT_TTL_HOURS == 24
    assert settings.RATE_LIMIT_FILES == 5
    assert settings.RATE_LIMIT_WINDOW_MINUTES == 10
    assert settings.PARSER_DEBUG is False
    assert settings.APP_ENV == "development"
    assert settings.is_development is True
    assert settings.is_production is False


def test_settings_admin_ids_parser():
    """Verify ADMIN_TELEGRAM_IDS parsing from comma-separated string."""
    settings = Settings(ADMIN_TELEGRAM_IDS="111, 222, 333")  # type: ignore
    assert settings.ADMIN_TELEGRAM_IDS == [111, 222, 333]

    empty_settings = Settings(ADMIN_TELEGRAM_IDS="")  # type: ignore
    assert empty_settings.ADMIN_TELEGRAM_IDS == []


def test_feature_flags_defaults():
    """Verify default feature flag values."""
    flags = FeatureFlags()
    assert flags.PORTAL_ENABLED is False
    assert flags.ADMIN_ENABLED is True
    assert flags.REFERRAL_ENABLED is True
    assert flags.IMAGE_EXPORT_ENABLED is True
    assert flags.HTML_EXPORT_ENABLED is True


def test_get_settings_cached():
    """Verify get_settings returns singleton cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_get_feature_flags_cached():
    """Verify get_feature_flags returns singleton cached instance."""
    f1 = get_feature_flags()
    f2 = get_feature_flags()
    assert f1 is f2


def test_sample_fixtures(sample_schedule_report: ScheduleReport, sample_excel_path):
    """Verify conftest fixtures load properly."""
    assert sample_schedule_report.total_courses == 1
    assert sample_schedule_report.total_units == 3.0
    assert sample_schedule_report.has_conflicts is False
    assert sample_excel_path.exists()
