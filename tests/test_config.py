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


def test_settings_port_and_database_url_normalization():
    """Verify Railway port and PostgreSQL URL normalization."""
    # Default port
    settings = Settings()
    assert settings.PORT == 8000

    # Railway standard postgres:// URL
    railway_url_1 = "postgres://postgres:secret123@roundhouse.proxy.rlwy.net:54321/railway"
    s1 = Settings(DATABASE_URL=railway_url_1)
    assert s1.DATABASE_URL == "postgresql+asyncpg://postgres:secret123@roundhouse.proxy.rlwy.net:54321/railway"

    # Railway postgresql:// URL without async driver
    railway_url_2 = "postgresql://postgres:secret123@postgres.railway.internal:5432/railway"
    s2 = Settings(DATABASE_URL=railway_url_2)
    assert s2.DATABASE_URL == "postgresql+asyncpg://postgres:secret123@postgres.railway.internal:5432/railway"

    # Already asyncpg URL
    asyncpg_url = "postgresql+asyncpg://user:pass@localhost:5432/db"
    s3 = Settings(DATABASE_URL=asyncpg_url)
    assert s3.DATABASE_URL == asyncpg_url

    # SQLite URL untouched
    sqlite_url = "sqlite+aiosqlite:///./storage/custom.db"
    s4 = Settings(DATABASE_URL=sqlite_url)
    assert s4.DATABASE_URL == sqlite_url


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
